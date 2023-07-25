from grpclib.client import Channel

from greenfield_python_sdk.protos.cosmos.params.v1beta1 import (
    QueryParamsRequest,
    QueryParamsResponse,
    QueryStub,
    QuerySubspacesRequest,
    QuerySubspacesResponse,
)


class Params:
    def __init__(self, channel: Channel):
        self.query_stub = QueryStub(channel)

    async def get_params(self, request: QueryParamsRequest) -> QueryParamsResponse:
        response = await self.query_stub.params(request)
        return response

    async def get_subspaces(self) -> QuerySubspacesResponse:
        request = QuerySubspacesRequest()
        response = await self.query_stub.subspaces(request)
        return response
