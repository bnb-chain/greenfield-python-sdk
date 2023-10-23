import asyncio
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Optional, Tuple

from betterproto.lib.google.protobuf import Any as AnyMessage

from greenfield_python_sdk.blockchain_client import BlockchainClient
from greenfield_python_sdk.key_manager import KeyManager
from greenfield_python_sdk.models.eip712_messages.sp.sp_url import (
    COSMOS_GRANT,
    CREATE_STORAGE_PROVIDER,
    GRANT_DEPOSIT,
    SUBMIT_PROPOSAL,
    UPDATE_SP_STORAGE_PRICE,
)
from greenfield_python_sdk.models.storage_provider import CreateStorageProviderOptions, GrantDepositOptions
from greenfield_python_sdk.protos.cosmos.auth.v1beta1 import QueryModuleAccountByNameRequest
from greenfield_python_sdk.protos.cosmos.authz.v1beta1 import Grant, MsgGrant
from greenfield_python_sdk.protos.cosmos.base.v1beta1 import Coin
from greenfield_python_sdk.protos.cosmos.gov.v1 import MsgSubmitProposal
from greenfield_python_sdk.protos.cosmos.tx.v1beta1 import GetTxRequest
from greenfield_python_sdk.protos.greenfield.sp import (
    DepositAuthorization,
    Description,
    MsgCreateStorageProvider,
    MsgUpdateSpStoragePrice,
    QuerySpStoragePriceRequest,
    QueryStorageProviderRequest,
    SpStoragePrice,
    Status,
)
from greenfield_python_sdk.protos.greenfield.sp import StorageProvider as SpStorageProvider
from greenfield_python_sdk.storage_client import StorageClient


class StorageProvider:
    blockchain_client: BlockchainClient
    key_manager: KeyManager
    storage_client: StorageClient

    def __init__(self, blockchain_client, key_manager, storage_client):
        self.blockchain_client = blockchain_client
        self.key_manager = key_manager
        self.storage_client = storage_client

    async def list_storage_providers(self, in_service: Optional[bool] = False) -> List[SpStorageProvider]:
        response = await self.blockchain_client.sp.get_storage_providers()
        if response.sps is None:
            raise Exception("Storage providers not found")

        sps = response.to_pydict()["sps"]
        if in_service:
            filtered_sps = []
            for sp in sps:
                if sp.get("status", 0) == Status.STATUS_IN_SERVICE:
                    filtered_sps.append(sp)
            return filtered_sps
        return sps

    async def get_storage_provider_info(self, sp_id: int) -> SpStorageProvider:
        response = await self.blockchain_client.sp.get_storage_provider(QueryStorageProviderRequest(id=sp_id))
        if response.storage_provider is None:
            raise Exception("Storage provider not found")

        return response.storage_provider

    async def get_storage_price(self, sp_addr: str) -> SpStoragePrice:
        response = await self.blockchain_client.sp.get_sp_storage_price(QuerySpStoragePriceRequest(sp_addr))
        if response.sp_storage_price is None:
            raise Exception("Storage price not found")

        return response.sp_storage_price

    async def grant_deposit_for_storage_provider(
        self, sp_addr: str, deposit_amount: int, opts: GrantDepositOptions
    ) -> str:
        gov_module = await self.blockchain_client.cosmos.auth.get_module_account_by_name(
            QueryModuleAccountByNameRequest(name="gov")
        )
        gov_module_address = gov_module.account.value.decode()
        gov_module_address = gov_module_address[4 : len(gov_module_address) - 15]

        authorization_value = DepositAuthorization(
            max_deposit=Coin(denom="BNB", amount=str(deposit_amount)), sp_address=sp_addr
        )
        authorization = AnyMessage(type_url=GRANT_DEPOSIT, value=bytes(authorization_value))
        msg_grant = MsgGrant(
            granter=self.key_manager.address,
            grantee=gov_module_address,
            grant=Grant(
                authorization=authorization,
                expiration=datetime.now() + timedelta(days=1),
            ),
        )

        response = await self.blockchain_client.broadcast_message(message=msg_grant, type_url=COSMOS_GRANT)
        return response

    async def create_storage_provider(
        self,
        funding_addr: str,
        seal_addr: str,
        approval_addr: str,
        gc_addr: str,
        maintenance_addr: str,
        endpoint: str,
        deposit_amount: int,
        description: Description,
        bls_key: str,
        bls_proof: str,
        opts: CreateStorageProviderOptions,
    ) -> Tuple[int, str]:
        gov_module = await self.blockchain_client.cosmos.auth.get_module_account_by_name(
            QueryModuleAccountByNameRequest(name="gov")
        )
        gov_module_address = gov_module.account.value.decode()
        gov_module_address = gov_module_address[4 : len(gov_module_address) - 15]

        if opts.proposal_deposit_amount is None:
            opts.proposal_deposit_amount = 1000000000000000000

        if opts.read_price is None:
            opts.read_price = 1

        if opts.store_price is None:
            opts.store_price = 1

        create_sp = MsgCreateStorageProvider(
            creator=gov_module_address,
            description=description,
            sp_address=self.key_manager.address,
            funding_address=funding_addr,
            seal_address=seal_addr,
            approval_address=approval_addr,
            gc_address=gc_addr,
            maintenance_address=maintenance_addr,
            endpoint=endpoint,
            deposit=Coin(denom="BNB", amount=str(deposit_amount)),
            read_price=str(opts.read_price * 10**18),
            free_read_quota=opts.free_read_quota,
            store_price=str(opts.store_price * 10**18),
            bls_key=bls_key,
            bls_proof=bls_proof,
        )
        msg_create_sp = AnyMessage(type_url=CREATE_STORAGE_PROVIDER, value=bytes(create_sp))
        msg_submit_proposal = MsgSubmitProposal(
            initial_deposit=[Coin(denom="BNB", amount=str(opts.proposal_deposit_amount))],
            proposer=self.key_manager.address,
            metadata=opts.proposal_meta_data,
            title=opts.proposal_title,
            summary=opts.proposal_summary,
            messages=[msg_create_sp],
        )
        hash = await self.blockchain_client.broadcast_message(
            message=msg_submit_proposal,
            type_url=SUBMIT_PROPOSAL,
        )
        await asyncio.sleep(10)
        request = GetTxRequest(hash=hash)
        resp = await self.blockchain_client.cosmos.tx.get_tx(request)

        for logs in resp.tx_response.logs:
            for events in logs.events:
                for attributes in events.attributes:
                    if attributes.key == "proposal_id":
                        proposal_id = int(attributes.value)
                        return proposal_id, hash
        raise Exception("ProposalID not found")

    async def update_sp_storage_price(
        self, sp_addr: str, read_price: Decimal, store_price: Decimal, free_read_quota: int
    ) -> str:
        msg_update_sp_storage_price = MsgUpdateSpStoragePrice(
            sp_address=sp_addr,
            read_price=str(read_price * 10**18),
            free_read_quota=free_read_quota,
            store_price=str(store_price * 10**18),
        )
        hash = await self.blockchain_client.broadcast_message(
            message=msg_update_sp_storage_price,
            type_url=UPDATE_SP_STORAGE_PRICE,
        )

        return hash
