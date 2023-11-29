import base64
from typing import Optional

import aiohttp
from betterproto import Casing
from betterproto.lib.google.protobuf import Any as AnyMessage
from grpclib.client import Channel

from greenfield_python_sdk.blockchain._cosmos.tx import SimulateRequest
from greenfield_python_sdk.blockchain.bridge import Bridge
from greenfield_python_sdk.blockchain.challenge import Challenge
from greenfield_python_sdk.blockchain.cosmos import Cosmos
from greenfield_python_sdk.blockchain.payment import Payment
from greenfield_python_sdk.blockchain.permission import Permission
from greenfield_python_sdk.blockchain.sp import Sp
from greenfield_python_sdk.blockchain.storage import Storage
from greenfield_python_sdk.blockchain.tendermint import Tendermint
from greenfield_python_sdk.blockchain.utils import CustomChannel
from greenfield_python_sdk.blockchain.virtual_group import VirtualGroup
from greenfield_python_sdk.config import NetworkConfiguration
from greenfield_python_sdk.key_manager import KeyManager
from greenfield_python_sdk.models.broadcast import BroadcastMode
from greenfield_python_sdk.models.eip712_messages.storage.bucket_url import CREATE_BUCKET, MIGRATE_BUCKET
from greenfield_python_sdk.models.eip712_messages.storage.object_url import CREATE_OBJECT
from greenfield_python_sdk.models.transaction import BroadcastOption
from greenfield_python_sdk.protos.cosmos.base.v1beta1 import Coin
from greenfield_python_sdk.protos.cosmos.crypto.secp256k1 import PubKey
from greenfield_python_sdk.protos.cosmos.tx.signing.v1beta1 import SignMode
from greenfield_python_sdk.protos.cosmos.tx.v1beta1 import (
    AuthInfo,
    Fee,
    ModeInfo,
    ModeInfoSingle,
    SignerInfo,
    Tx,
    TxBody,
)
from greenfield_python_sdk.sign_utils import get_signature


class BlockchainClient:
    def __init__(
        self,
        network_configuration: NetworkConfiguration,
        channel: Optional[Channel] = None,
        key_manager: Optional[KeyManager] = None,
    ):
        self.host = network_configuration.host
        self.port = network_configuration.port
        self.base_url = f"{self.host}:{self.port}"
        self.chain_id = network_configuration.chain_id

        self.channel = channel
        self.key_manager = key_manager

    async def __aenter__(self):
        if not self.channel:
            self.channel = CustomChannel(self.host, self.port)

        # Initialize Tendermint Core
        self.tendermint = Tendermint(self.channel)

        # Initialize Greenfield stubs (Tendermint Core X)
        self.bridge = Bridge(self.channel)
        self.challenge = Challenge(self.channel)
        self.payment = Payment(self.channel)
        self.permission = Permission(self.channel)
        self.sp = Sp(self.channel)
        self.storage = Storage(self.channel)
        self.virtual_group = VirtualGroup(self.channel)

        # Initialize Cosmos-SDK
        self.cosmos = Cosmos(self.channel)

        return self

    @property
    def connected(self) -> bool:
        if self.channel:
            return self.channel._connected
        return False

    async def build_tx(
        self,
        message,
        type_url: str,
        fee: Optional[Fee] = None,
    ) -> Tx:
        if not self.key_manager:
            raise KeyError("To build txs you need to add a key_manager to the BlockchainClient")

        if not fee:
            # Note: This fee is temporal, as it will get replaced later automatically with a correct amount based on the simulated tx
            fee = Fee(
                amount=[Coin(denom="BNB", amount="10000000000000")],
                gas_limit=2000,
                payer=self.key_manager.address,
            )
        if type_url == CREATE_BUCKET or type_url == CREATE_OBJECT:  # TODO: Move to other place
            sp_approval = base64.b64decode(message.primary_sp_approval.sig)
            message.primary_sp_approval.sig = bytes(sp_approval)

        if type_url == MIGRATE_BUCKET:
            sp_approval = base64.b64decode(message.dst_primary_sp_approval.sig)
            message.dst_primary_sp_approval.sig = bytes(sp_approval)

        wrapped_message = AnyMessage(
            type_url=type_url,
            value=bytes(message),
        )

        body = TxBody(messages=[wrapped_message])
        auth_info = AuthInfo(
            signer_infos=[
                SignerInfo(
                    public_key=AnyMessage(
                        type_url="/cosmos.crypto.eth.ethsecp256k1.PubKey",
                        value=bytes(PubKey(key=self.key_manager.account.public_key)),
                    ),
                    mode_info=ModeInfo(single=ModeInfoSingle(mode=SignMode.SIGN_MODE_EIP_712)),
                    sequence=self.key_manager.account.next_sequence,
                )
            ],
            fee=fee,
        )

        tx = Tx(
            body=body,
            auth_info=auth_info,
            signatures=[b""],
        )

        return tx

    async def simulate_tx(self, tx: Tx):
        resp = await self.cosmos.tx.simulate(request=SimulateRequest(tx_bytes=bytes(tx)))
        return resp

    async def simulate_raw_tx(self, tx_bytes: bytes):
        resp = await self.cosmos.tx.simulate(request=SimulateRequest(tx_bytes=tx_bytes))
        return resp

    async def broadcast_tx(self, tx: Tx, mode: BroadcastMode = BroadcastMode.BROADCAST_MODE_SYNC) -> str:
        tx_hash = await self.broadcast_raw_tx(tx_bytes=bytes(tx), mode=mode)
        return tx_hash

    async def broadcast_raw_tx(self, tx_bytes: bytes, mode: BroadcastMode = BroadcastMode.BROADCAST_MODE_SYNC) -> str:
        async with aiohttp.ClientSession() as session:
            # TODO: Add broadcast mode
            response = await session.request(
                "GET",
                f"{self.base_url}/broadcast_tx_sync",
                params={"tx": "0x" + tx_bytes.hex()},
            )
            data = await response.json()

            if data["result"]["code"] != 0:
                raise Exception("Transaction error: ", data["result"]["log"])
            self.key_manager.account.increase_sequence()
            return data["result"]["hash"]

    async def build_tx_from_message(
        self,
        message,
        type_url: str,
        fee: Optional[Fee] = None,
        broadcast_option: Optional[BroadcastOption] = None,
    ):
        tx = await self.build_tx(message=message, type_url=type_url, fee=fee)

        signature_pre = await get_signature(self.key_manager, tx, message, self.chain_id, broadcast_option)
        tx.signatures = [signature_pre]
        try:
            simulation = await self.simulate_tx(tx)
            tx.auth_info.fee.gas_limit = simulation.gas_info.gas_used
            tx.auth_info.fee.amount[0].amount = str(
                int(simulation.gas_info.min_gas_price[:-3]) * int(simulation.gas_info.gas_used)
            )
        except Exception as e:
            if e.args[0] != "":
                raise Exception(f"Error at simulation: {e}")
            tx.auth_info.fee.gas_limit = 20000000
            tx.auth_info.fee.amount[0].amount = "100000000000000000"

        signature = await get_signature(self.key_manager, tx, message, self.chain_id, broadcast_option)
        tx.signatures = [signature]
        return tx

    async def broadcast_message(
        self,
        message,
        type_url: str,
        fee: Optional[Fee] = None,
        broadcast_option: Optional[BroadcastOption] = None,
    ):
        tx = await self.build_tx_from_message(
            message=message,
            type_url=type_url,
            fee=fee,
            broadcast_option=broadcast_option,
        )

        if tx.auth_info.fee.payer == self.key_manager.address:
            del tx.auth_info.fee.payer

        tx_hash = await self.broadcast_tx(tx)
        return tx_hash

    async def get_active_sps(self):
        response = await self.sp.get_storage_providers()
        return (
            [sp for sp in response.to_pydict(casing=Casing.SNAKE)["sps"] if "bnbchain.org" in sp["endpoint"]]
            if "testnet" in self.host
            else [sp for sp in response.to_pydict(casing=Casing.SNAKE)["sps"]]
        )

    async def close(self):
        pass

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
