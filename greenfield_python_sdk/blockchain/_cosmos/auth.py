from grpclib.client import Channel

from greenfield_python_sdk.protos.cosmos.auth.v1beta1 import (
    AddressBytesToStringRequest,
    AddressBytesToStringResponse,
    AddressStringToBytesRequest,
    AddressStringToBytesResponse,
    QueryAccountAddressByIdRequest,
    QueryAccountAddressByIdResponse,
    QueryAccountRequest,
    QueryAccountResponse,
    QueryAccountsRequest,
    QueryAccountsResponse,
    QueryModuleAccountByNameRequest,
    QueryModuleAccountByNameResponse,
    QueryModuleAccountsRequest,
    QueryModuleAccountsResponse,
    QueryParamsRequest,
    QueryParamsResponse,
    QueryStub,
)


class Auth:
    def __init__(self, channel: Channel):
        self.query_stub = QueryStub(channel)

    async def get_params(self) -> QueryParamsResponse:
        request = QueryParamsRequest()
        response = await self.query_stub.params(request)
        return response

    async def get_accounts(self, request: QueryAccountsRequest = QueryAccountsRequest()) -> QueryAccountsResponse:
        response = await self.query_stub.accounts(request)
        return response

    async def get_account(self, request: QueryAccountRequest) -> QueryAccountResponse:
        response = await self.query_stub.account(request)
        return response

    async def get_account_address_by_id(
        self, request: QueryAccountAddressByIdRequest
    ) -> QueryAccountAddressByIdResponse:
        response = await self.query_stub.account_address_by_id(request)
        return response

    async def get_module_accounts(self) -> QueryModuleAccountsResponse:
        request = QueryModuleAccountsRequest()
        response = await self.query_stub.module_accounts(request)
        return response

    async def get_module_account_by_name(
        self, request: QueryModuleAccountByNameRequest
    ) -> QueryModuleAccountByNameResponse:
        response = await self.query_stub.module_account_by_name(request)
        return response

    async def address_bytes_to_string(self, request: AddressBytesToStringRequest) -> AddressBytesToStringResponse:
        response = await self.query_stub.address_bytes_to_string(request)
        return response

    async def address_string_to_bytes(self, request: AddressStringToBytesRequest) -> AddressStringToBytesResponse:
        response = await self.query_stub.address_string_to_bytes(request)
        return response
