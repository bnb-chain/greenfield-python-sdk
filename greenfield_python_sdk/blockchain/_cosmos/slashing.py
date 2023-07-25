from grpclib.client import Channel

from greenfield_python_sdk.protos.cosmos.slashing.v1beta1 import (
    QueryParamsRequest,
    QueryParamsResponse,
    QuerySigningInfoRequest,
    QuerySigningInfoResponse,
    QuerySigningInfosRequest,
    QuerySigningInfosResponse,
    QueryStub,
)


class Slashing:
    def __init__(self, channel: Channel):
        self.query_stub = QueryStub(channel)

    async def get_params(self) -> QueryParamsResponse:
        request = QueryParamsRequest()
        response = await self.query_stub.params(request)
        return response

    async def get_signing_info(self, request: QuerySigningInfoRequest) -> QuerySigningInfoResponse:
        response = await self.query_stub.signing_info(request)
        return response

    async def get_signing_infos(
        self, request: QuerySigningInfosRequest = QuerySigningInfosRequest()
    ) -> QuerySigningInfosResponse:
        response = await self.query_stub.signing_infos(request)
        return response
