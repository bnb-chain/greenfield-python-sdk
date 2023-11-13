from grpclib.client import Channel

from greenfield_python_sdk.protos.greenfield.payment import (
    QueryDynamicBalanceRequest,
    QueryDynamicBalanceResponse,
    QueryGetStreamRecordRequest,
    QueryGetStreamRecordResponse,
    QueryParamsRequest,
    QueryParamsResponse,
    QueryPaymentAccountRequest,
    QueryPaymentAccountResponse,
    QueryPaymentAccountsByOwnerRequest,
    QueryPaymentAccountsByOwnerResponse,
    QueryPaymentAccountsRequest,
    QueryPaymentAccountsResponse,
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

    async def get_dynamic_balance(self, request: QueryDynamicBalanceRequest) -> QueryDynamicBalanceResponse:
        response = await self.query_stub.dynamic_balance(request)
        return response

    async def get_payment_account(self, request: QueryPaymentAccountRequest) -> QueryPaymentAccountResponse:
        response = await self.query_stub.payment_account(request)
        return response

    async def get_payment_accounts_by_owner(
        self, request: QueryPaymentAccountsByOwnerRequest
    ) -> QueryPaymentAccountsByOwnerResponse:
        response = await self.query_stub.payment_accounts_by_owner(request)
        return response

    async def get_payment_accounts(self, request: QueryPaymentAccountsRequest) -> QueryPaymentAccountsResponse:
        response = await self.query_stub.payment_accounts(request)
        return response
