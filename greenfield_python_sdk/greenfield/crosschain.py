from typing import List

from greenfield_python_sdk.blockchain._cosmos.crosschain import QueryReceiveSequenceRequest, QuerySendSequenceRequest
from greenfield_python_sdk.blockchain_client import BlockchainClient
from greenfield_python_sdk.protos.cosmos.base.v1beta1 import Coin
from greenfield_python_sdk.protos.cosmos.oracle.v1 import MsgClaim, QueryInturnRelayerResponse
from greenfield_python_sdk.protos.greenfield.bridge import MsgTransferOut
from greenfield_python_sdk.protos.greenfield.storage import MsgMirrorBucket, MsgMirrorGroup, MsgMirrorObject
from greenfield_python_sdk.storage_client import StorageClient


class CrossChain:
    def __init__(self, blockchain_client: BlockchainClient, storage_client: StorageClient):
        self.blockchain_client = blockchain_client
        self.storage_client = storage_client

    async def transfer_out(
        self,
        to_address: str,
        amount: Coin,
    ):
        msg_transfer_out = MsgTransferOut(from_=self.storage_client.key_manager.address, to=to_address, amount=amount)
        tx = await self.blockchain_client.broadcast_message(
            msg_transfer_out, type_url="/greenfield.bridge.MsgTransferOut"
        )
        return tx

    async def claims(
        self,
        src_chain_id: int,
        dest_chain_id: int,
        sequence: int,
        timestamp: int,
        payload: bytes,
        vote_addr_set: List[int],
        agg_signature: bytes,
    ):
        msg = MsgClaim(
            from_address=self.storage_client.key_manager.address,
            src_chain_id=src_chain_id,
            dest_chain_id=dest_chain_id,
            sequence=sequence,
            timestamp=timestamp,
            payload=payload,
            vote_addr_set=vote_addr_set,
            agg_signature=agg_signature,
        )
        tx = await self.blockchain_client.broadcast_message(msg)

        return tx

    async def get_channel_send_sequence(self, channel_id: int) -> int:
        request = QuerySendSequenceRequest(channel_id)
        response = await self.blockchain_client.cosmos.crosschain.get_send_sequence(request=request)
        return response.sequence

    async def get_channel_receive_sequence(self, channel_id: int) -> int:
        request = QueryReceiveSequenceRequest(channel_id)
        response = await self.blockchain_client.cosmos.crosschain.get_receive_sequence(request=request)
        return response.sequence

    async def get_inturn_relayer(self) -> QueryInturnRelayerResponse:
        return await self.blockchain_client.cosmos.oracle.get_inturn_relayer()

    async def get_crosschain_package(self, channel_id: int, sequence: int) -> bytes:
        response = await self.blockchain_client.cosmos.crosschain.get_crosschain_package(channel_id, sequence)

        return response.package

    async def mirror_group(
        self,
        group_id: str,
        group_name: str,
    ):
        msg_mirror_group = MsgMirrorGroup(
            operator=self.storage_client.key_manager.address,
            id=group_id,
        )

        tx = await self.blockchain_client.broadcast_message(
            msg_mirror_group, type_url="/greenfield.storage.MsgMirrorGroup"
        )

        return tx

    async def mirror_bucket(
        self,
        bucket_id: str,
        bucket_name: str,
    ):
        msg_mirror_bucket = MsgMirrorBucket(
            operator=self.storage_client.key_manager.address,
            id=bucket_id,
            bucket_name=bucket_name,
        )

        tx = await self.blockchain_client.broadcast_message(
            msg_mirror_bucket, type_url="/greenfield.storage.MsgMirrorBucket"
        )

        return tx

    async def mirror_object(
        self,
        object_id: str,
        bucket_name: str,
        object_name: str,
    ):
        msg_mirror_object = MsgMirrorObject(
            operator=self.storage_client.key_manager.address,
            id=object_id,
            bucket_name=bucket_name,
            object_name=object_name,
        )

        tx = await self.blockchain_client.broadcast_message(
            msg_mirror_object, type_url="/greenfield.storage.MsgMirrorObject"
        )

        return tx
