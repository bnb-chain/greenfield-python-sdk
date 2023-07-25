from grpclib.client import Channel

from greenfield_python_sdk.protos.cosmos.tx.v1beta1 import (
    GetBlockWithTxsRequest,
    GetBlockWithTxsResponse,
    GetTxRequest,
    GetTxResponse,
    GetTxsEventRequest,
    GetTxsEventResponse,
    ServiceStub,
    SimulateRequest,
    SimulateResponse,
)


class Tx:
    def __init__(self, channel: Channel):
        self.query_stub = ServiceStub(channel)

    async def get_txs_event(self, request: GetTxsEventRequest) -> GetTxsEventResponse:
        response = await self.query_stub.get_txs_event(request)
        return response

    async def simulate(self, request: SimulateRequest) -> SimulateResponse:
        response = await self.query_stub.simulate(request)
        return response

    async def get_tx(self, request: GetTxRequest) -> GetTxResponse:
        response = await self.query_stub.get_tx(request)
        return response

    async def get_block_with_txs(self, request: GetBlockWithTxsRequest) -> GetBlockWithTxsResponse:
        response = await self.query_stub.get_block_with_txs(request)
        return response
