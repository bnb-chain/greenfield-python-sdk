from grpclib.client import Channel

from greenfield_python_sdk.protos.cosmos.feegrant.v1beta1 import (
    QueryAllowanceRequest,
    QueryAllowanceResponse,
    QueryAllowancesByGranterRequest,
    QueryAllowancesByGranterResponse,
    QueryAllowancesRequest,
    QueryAllowancesResponse,
    QueryStub,
)


class FeeGrant:
    def __init__(self, channel: Channel):
        self.query_stub = QueryStub(channel)

    async def get_allowance(self, query_allowance_request: QueryAllowanceRequest) -> QueryAllowanceResponse:
        response = await self.query_stub.allowance(query_allowance_request)
        return response

    async def get_allowances(self, query_allowances_request: QueryAllowancesRequest) -> QueryAllowancesResponse:
        response = await self.query_stub.allowances(query_allowances_request)
        return response

    async def get_allowances_by_granter(
        self, query_allowances_by_granter_request: QueryAllowancesByGranterRequest
    ) -> QueryAllowancesByGranterResponse:
        response = await self.query_stub.allowances_by_granter(query_allowances_by_granter_request)
        return response
