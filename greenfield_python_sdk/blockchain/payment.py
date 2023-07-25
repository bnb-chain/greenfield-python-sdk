from grpclib.client import Channel

from greenfield_python_sdk.protos.greenfield.payment import (
    QueryAllAutoSettleRecordRequest,
    QueryAllAutoSettleRecordResponse,
    QueryAllPaymentAccountCountRequest,
    QueryAllPaymentAccountCountResponse,
    QueryAllPaymentAccountRequest,
    QueryAllPaymentAccountResponse,
    QueryAllStreamRecordRequest,
    QueryAllStreamRecordResponse,
    QueryDynamicBalanceRequest,
    QueryDynamicBalanceResponse,
    QueryGetPaymentAccountCountRequest,
    QueryGetPaymentAccountCountResponse,
    QueryGetPaymentAccountRequest,
    QueryGetPaymentAccountResponse,
    QueryGetPaymentAccountsByOwnerRequest,
    QueryGetPaymentAccountsByOwnerResponse,
    QueryGetStreamRecordRequest,
    QueryGetStreamRecordResponse,
    QueryParamsRequest,
    QueryParamsResponse,
    QueryStub,
)


class Payment:
    def __init__(self, channel: Channel):
        self.query_stub = QueryStub(channel)

    async def get_params(self) -> QueryParamsResponse:
        request = QueryParamsRequest()
        response = await self.query_stub.params(request)
        return response

    async def get_stream_record(self, request: QueryGetStreamRecordRequest) -> QueryGetStreamRecordResponse:
        response = await self.query_stub.stream_record(request)
        return response

    async def get_stream_record_all(
        self, request: QueryAllStreamRecordRequest = QueryAllStreamRecordRequest()
    ) -> QueryAllStreamRecordResponse:
        response = await self.query_stub.stream_record_all(request)
        return response

    async def get_payment_account_count(
        self, request: QueryGetPaymentAccountCountRequest
    ) -> QueryGetPaymentAccountCountResponse:
        response = await self.query_stub.payment_account_count(request)
        return response

    async def get_payment_account_count_all(
        self, request: QueryAllPaymentAccountCountRequest = QueryAllPaymentAccountCountRequest()
    ) -> QueryAllPaymentAccountCountResponse:
        response = await self.query_stub.payment_account_count_all(request)
        return response

    async def get_payment_account(self, request: QueryGetPaymentAccountRequest) -> QueryGetPaymentAccountResponse:
        response = await self.query_stub.payment_account(request)
        return response

    async def get_payment_account_all(
        self, request: QueryAllPaymentAccountRequest = QueryAllPaymentAccountRequest()
    ) -> QueryAllPaymentAccountResponse:
        response = await self.query_stub.payment_account_all(request)
        return response

    async def get_dynamic_balance(self, request: QueryDynamicBalanceRequest) -> QueryDynamicBalanceResponse:
        response = await self.query_stub.dynamic_balance(request)
        return response

    async def get_get_payment_accounts_by_owner(
        self, request: QueryGetPaymentAccountsByOwnerRequest
    ) -> QueryGetPaymentAccountsByOwnerResponse:
        response = await self.query_stub.get_payment_accounts_by_owner(request)
        return response

    async def get_auto_settle_record_all(
        self, request: QueryAllAutoSettleRecordRequest = QueryAllAutoSettleRecordRequest()
    ) -> QueryAllAutoSettleRecordResponse:
        response = await self.query_stub.auto_settle_record_all(request)
        return response
