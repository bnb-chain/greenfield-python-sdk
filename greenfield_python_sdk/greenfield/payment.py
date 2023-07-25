from eth_utils import to_checksum_address

from greenfield_python_sdk.blockchain_client import BlockchainClient
from greenfield_python_sdk.protos.greenfield.payment import (
    MsgDeposit,
    MsgDisableRefund,
    MsgWithdraw,
    QueryGetStreamRecordRequest,
    StreamRecord,
)
from greenfield_python_sdk.storage_client import StorageClient


class Payment:
    def __init__(self, blockchain_client: BlockchainClient, storage_client: StorageClient):
        self.blockchain_client = blockchain_client
        self.storage_client = storage_client

    async def get_stream_record(self, stream_address: str) -> StreamRecord:
        stream_address = to_checksum_address(stream_address)

        request = QueryGetStreamRecordRequest(account=stream_address)
        response = await self.blockchain_client.payment.get_stream_record(request)

        return response

    async def deposit(self, to_address: str, amount: int) -> str:
        creator = to_checksum_address(self.storage_client.key_manager.address)
        to_address = to_checksum_address(to_address)

        msg_deposit = MsgDeposit(
            creator=creator,
            to=to_address,
            amount=str(amount),
        )
        tx = await self.blockchain_client.broadcast_message(msg_deposit, type_url="/greenfield.payment.MsgDeposit")
        return tx

    async def withdraw(self, from_address: str, amount: int) -> str:
        creator = to_checksum_address(self.storage_client.key_manager.address)
        from_address = to_checksum_address(from_address)

        msg_deposit = MsgWithdraw(
            creator=creator,
            from_=from_address,
            amount=str(amount),
        )
        tx = await self.blockchain_client.broadcast_message(msg_deposit, type_url="/greenfield.payment.MsgWithdraw")

        return tx

    async def disable_refund(self, address: str) -> str:
        creator = to_checksum_address(self.storage_client.key_manager.address)
        address = to_checksum_address(address)

        msg_disable_refund = MsgDisableRefund(
            owner=creator,
            addr=address,
        )

        tx = await self.blockchain_client.broadcast_message(
            msg_disable_refund, type_url="/greenfield.payment.MsgDisableRefund"
        )

        return tx
