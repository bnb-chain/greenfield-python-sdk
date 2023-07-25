from grpclib.client import Channel

from greenfield_python_sdk.protos.cosmos.bank.v1beta1 import (
    QueryAllBalancesRequest,
    QueryAllBalancesResponse,
    QueryBalanceRequest,
    QueryBalanceResponse,
    QueryDenomMetadataRequest,
    QueryDenomMetadataResponse,
    QueryDenomOwnersRequest,
    QueryDenomOwnersResponse,
    QueryDenomsMetadataRequest,
    QueryDenomsMetadataResponse,
    QueryParamsRequest,
    QueryParamsResponse,
    QuerySpendableBalancesRequest,
    QuerySpendableBalancesResponse,
    QueryStub,
    QuerySupplyOfRequest,
    QuerySupplyOfResponse,
    QueryTotalSupplyRequest,
    QueryTotalSupplyResponse,
)


class Bank:
    def __init__(self, channel: Channel):
        self.query_stub = QueryStub(channel)

    async def get_balance(self, request: QueryBalanceRequest) -> QueryBalanceResponse:
        response = await self.query_stub.balance(request)
        return response

    async def get_all_balances(self, request: QueryAllBalancesRequest) -> QueryAllBalancesResponse:
        response = await self.query_stub.all_balances(request)
        return response

    async def get_spendable_balances(self, request: QuerySpendableBalancesRequest) -> QuerySpendableBalancesResponse:
        response = await self.query_stub.spendable_balances(request)
        return response

    async def get_total_supply(
        self, request: QueryTotalSupplyRequest = QueryTotalSupplyRequest()
    ) -> QueryTotalSupplyResponse:
        response = await self.query_stub.total_supply(request)
        return response

    async def get_supply_of(self, request: QuerySupplyOfRequest) -> QuerySupplyOfResponse:
        response = await self.query_stub.supply_of(request)
        return response

    async def get_params(self) -> QueryParamsResponse:
        request = QueryParamsRequest()
        response = await self.query_stub.params(request)
        return response

    async def get_denom_metadata(self, request: QueryDenomMetadataRequest) -> QueryDenomMetadataResponse:
        response = await self.query_stub.denom_metadata(request)
        return response

    async def get_denoms_metadata(
        self, request: QueryDenomsMetadataRequest = QueryDenomsMetadataRequest()
    ) -> QueryDenomsMetadataResponse:
        response = await self.query_stub.denoms_metadata(request)
        return response

    async def get_denom_owners(self, request: QueryDenomOwnersRequest) -> QueryDenomOwnersResponse:
        response = await self.query_stub.denom_owners(request)
        return response
