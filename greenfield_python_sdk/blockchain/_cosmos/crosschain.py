from grpclib.client import Channel

from greenfield_python_sdk.protos.cosmos.crosschain.v1 import (
    QueryCrossChainPackageRequest,
    QueryCrossChainPackageResponse,
    QueryParamsRequest,
    QueryParamsResponse,
    QueryReceiveSequenceRequest,
    QueryReceiveSequenceResponse,
    QuerySendSequenceRequest,
    QuerySendSequenceResponse,
    QueryStub,
)


class Crosschain:
    def __init__(self, channel: Channel):
        self.query_stub = QueryStub(channel)

    async def get_params(self) -> QueryParamsResponse:
        request = QueryParamsRequest()
        response = await self.query_stub.params(request)
        return response

    async def get_crosschain_package(self, channel_id: int, sequence: int) -> QueryCrossChainPackageResponse:
        request = QueryCrossChainPackageRequest(channel_id=channel_id, sequence=sequence)
        response = await self.query_stub.cross_chain_package(request)
        return response

    async def get_send_sequence(self, request: QuerySendSequenceRequest) -> QuerySendSequenceResponse:
        response = await self.query_stub.send_sequence(request)
        return response

    async def get_receive_sequence(self, request: QueryReceiveSequenceRequest) -> QueryReceiveSequenceResponse:
        response = await self.query_stub.receive_sequence(request)
        return response
