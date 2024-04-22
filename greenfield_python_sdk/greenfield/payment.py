from datetime import datetime, timedelta
from typing import List

import html_to_json
from eth_utils import to_checksum_address

from greenfield_python_sdk.blockchain_client import BlockchainClient
from greenfield_python_sdk.models.payment import ListUserPaymentAccountsOptions, ListUserPaymentAccountsResult
from greenfield_python_sdk.models.request import RequestMeta
from greenfield_python_sdk.protos.cosmos.base.query.v1beta1 import PageResponse as PaginationResponse
from greenfield_python_sdk.protos.greenfield.payment import (
    MsgDeposit,
    MsgDisableRefund,
    MsgWithdraw,
    PaymentAccount,
    QueryGetStreamRecordRequest,
    QueryPaymentAccountsRequest,
    StreamRecord,
)
from greenfield_python_sdk.storage_client import StorageClient
from greenfield_python_sdk.storage_provider.utils import convert_key, convert_value


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

    async def list_user_payment_accounts(
        self, opts: ListUserPaymentAccountsOptions
    ) -> List[ListUserPaymentAccountsResult]:
        query_parameters = {
            "user-payments": "",
        }
        account = opts.account
        if account == "":
            account = self.storage_client.key_manager.address

        expiry = (datetime.utcnow() + timedelta(seconds=1000)).strftime("%Y-%m-%dT%H:%M:%SZ")
        base_url = await self.storage_client.client.get_url(opts.endpoint, opts.sp_address)
        request_metadata = RequestMeta(
            disable_close_body=True,
            user_address=account,
            query_parameters=query_parameters,
            base_url=base_url,
            expiry_timestamp=expiry,
        ).model_dump()
        response = await self.storage_client.client.prepare_request(
            base_url,
            request_metadata,
            request_metadata["query_parameters"],
        )
        list_payment_accounts = html_to_json.convert(await response.text())["gfsplistuserpaymentaccountsresponse"][0]

        list_user_payment_accounts = []
        if "paymentaccounts" in list_payment_accounts:
            test = list_payment_accounts["paymentaccounts"]
            for test in list_payment_accounts["paymentaccounts"]:
                converted_data_list = {
                    convert_key(key): convert_value(key, value) if value[0] else "" for key, value in test.items()
                }
                fields = ["netflow_rate", "static_balance", "buffer_balance", "lock_balance", "frozen_netflow_rate"]
                for field in fields:
                    converted_data_list["stream_record"][field] = str(converted_data_list["stream_record"][field])
                list_user_payment_accounts.append(ListUserPaymentAccountsResult(**converted_data_list))
        return list_user_payment_accounts

    async def get_all_payment_accounts(self, pagination: PaginationResponse = None) -> List["PaymentAccount"]:
        request = QueryPaymentAccountsRequest(pagination)
        response = await self.blockchain_client.payment.get_payment_accounts(request)
        return response.payment_accounts
