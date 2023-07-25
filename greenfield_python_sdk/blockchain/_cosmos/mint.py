from grpclib.client import Channel

from greenfield_python_sdk.protos.cosmos.mint.v1beta1 import (
    QueryAnnualProvisionsRequest,
    QueryAnnualProvisionsResponse,
    QueryInflationRequest,
    QueryInflationResponse,
    QueryParamsRequest,
    QueryParamsResponse,
    QueryStub,
)


class Mint:
    def __init__(self, channel: Channel):
        self.query_stub = QueryStub(channel)

    async def get_params(self) -> QueryParamsResponse:
        request = QueryParamsRequest()
        response = await self.query_stub.params(request)
        return response

    async def get_inflation(self) -> QueryInflationResponse:
        request = QueryInflationRequest()
        response = await self.query_stub.inflation(request)
        return response

    async def get_annual_provisions(self) -> QueryAnnualProvisionsResponse:
        request = QueryAnnualProvisionsRequest()
        response = await self.query_stub.annual_provisions(request)
        return response
