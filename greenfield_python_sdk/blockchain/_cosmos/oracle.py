from grpclib.client import Channel

from greenfield_python_sdk.protos.cosmos.oracle.v1 import (
    QueryInturnRelayerRequest,
    QueryInturnRelayerResponse,
    QueryParamsRequest,
    QueryParamsResponse,
    QueryStub,
)


class Oracle:
    def __init__(self, channel: Channel):
        self.query_stub = QueryStub(channel)

    async def get_params(self) -> QueryParamsResponse:
        request = QueryParamsRequest()
        response = await self.query_stub.params(request)
        return response

    async def get_inturn_relayer(self) -> QueryInturnRelayerResponse:
        request = QueryInturnRelayerRequest()
        response = await self.query_stub.inturn_relayer(request)
        return response
