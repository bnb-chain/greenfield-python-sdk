from datetime import datetime
from typing import List, Union

from betterproto.lib.google.protobuf import Any as AnyMessage
from eth_utils import to_checksum_address

from greenfield_python_sdk.blockchain_client import BlockchainClient
from greenfield_python_sdk.protos.cosmos.base.v1beta1 import Coin
from greenfield_python_sdk.protos.cosmos.feegrant.v1beta1 import (
    AllowedMsgAllowance,
    BasicAllowance,
    Grant,
    MsgGrantAllowance,
    MsgRevokeAllowance,
    PeriodicAllowance,
    QueryAllowanceRequest,
    QueryAllowancesByGranterRequest,
    QueryAllowancesRequest,
)
from greenfield_python_sdk.storage_client import StorageClient


class FeeGrant:
    blockchain_client: BlockchainClient
    storage_client: StorageClient

    def __init__(self, blockchain_client, storage_client):
        self.blockchain_client = blockchain_client
        self.storage_client = storage_client

    async def grant_basic_allowance(self, grantee_address: str, spend_limit: int, expiration: datetime) -> str:
        grantee_address = to_checksum_address(grantee_address)

        spend_limit = [Coin(denom="BNB", amount=str(spend_limit))]

        allowance = BasicAllowance(
            spend_limit=spend_limit,
            expiration=expiration,
        )
        hash = await self.grant_allowance(grantee_address, allowance)

        return hash

    async def get_basic_allowance(self, granter_address: str, grantee_address: str) -> BasicAllowance:
        granter_address = to_checksum_address(granter_address)
        grantee_address = to_checksum_address(grantee_address)
        response = await self.get_allowance(granter_address=granter_address, grantee_address=grantee_address)
        return response.allowance

    async def grant_allowance(
        self, grantee_address: str, allowance: Union[BasicAllowance, PeriodicAllowance, AllowedMsgAllowance]
    ) -> str:
        grantee_address = to_checksum_address(grantee_address)

        if not isinstance(allowance, (BasicAllowance, PeriodicAllowance, AllowedMsgAllowance)):
            raise TypeError("allowance must be one of asicAllowance, PeriodicAllowance, AllowedMsgAllowance")

        wrapped_allowance = AnyMessage(
            type_url=f"/cosmos.feegrant.v1beta1.{type(allowance).__name__}",
            value=bytes(allowance),
        )

        message = MsgGrantAllowance(
            granter=self.storage_client.key_manager.address, grantee=grantee_address, allowance=wrapped_allowance
        )

        hash = await self.blockchain_client.broadcast_message(
            messages=[message], type_url=["/cosmos.feegrant.v1beta1.MsgGrantAllowance"]
        )

        return hash

    async def get_allowance(self, granter_address: str, grantee_address: str) -> "Grant":
        granter_address = to_checksum_address(granter_address)
        grantee_address = to_checksum_address(grantee_address)

        request = QueryAllowanceRequest(granter=granter_address, grantee=grantee_address)
        response = await self.blockchain_client.cosmos.feegrant.get_allowance(request)
        if response.allowance.allowance.type_url == "/cosmos.feegrant.v1beta1.BasicAllowance":
            response.allowance.allowance = BasicAllowance.FromString(response.allowance.allowance.value)
        else:
            response.allowance.allowance = PeriodicAllowance.FromString(response.allowance.allowance.value)

        return response.allowance

    async def get_allowances(self, grantee_address: str) -> List[Grant]:
        # TODO: Add pagination
        grantee_address = to_checksum_address(grantee_address)

        request = QueryAllowancesRequest(grantee=grantee_address)
        response = await self.blockchain_client.cosmos.feegrant.get_allowances(request)
        return response.allowances

    async def get_allowances_by_granter(self, granter_address: str) -> List[Grant]:
        # TODO: Add pagination
        granter_address = to_checksum_address(granter_address)

        request = QueryAllowancesByGranterRequest(granter=granter_address)
        response = await self.blockchain_client.cosmos.feegrant.get_allowances_by_granter(request)
        return response.allowances

    async def revoke_allowance(self, granter_address: str, grantee_address: str) -> str:
        granter_address = to_checksum_address(granter_address)
        grantee_address = to_checksum_address(grantee_address)

        message = MsgRevokeAllowance(granter=self.storage_client.key_manager.address, grantee=grantee_address)

        hash = await self.blockchain_client.broadcast_message(
            messages=[message], type_url=["/cosmos.feegrant.v1beta1.MsgRevokeAllowance"]
        )

        return hash
