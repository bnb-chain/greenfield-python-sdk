from grpclib.client import Channel

from greenfield_python_sdk.protos.cosmos.authz.v1beta1 import (
    QueryGranteeGrantsRequest,
    QueryGranteeGrantsResponse,
    QueryGranterGrantsRequest,
    QueryGranterGrantsResponse,
    QueryGrantsRequest,
    QueryGrantsResponse,
    QueryStub,
)


class Authz:
    def __init__(self, channel: Channel):
        self.query_stub = QueryStub(channel)

    async def get_grants(self, request: QueryGrantsRequest) -> QueryGrantsResponse:
        response = await self.query_stub.grants(request)
        return response

    async def get_granter_grants(self, request: QueryGranterGrantsRequest) -> QueryGranterGrantsResponse:
        response = await self.query_stub.granter_grants(request)
        return response

    async def get_grantee_grants(self, request: QueryGranteeGrantsRequest) -> QueryGranteeGrantsResponse:
        response = await self.query_stub.grantee_grants(request)
        return response
