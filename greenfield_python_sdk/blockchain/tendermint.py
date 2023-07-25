from grpclib.client import Channel

from greenfield_python_sdk.protos.cosmos.base.tendermint.v1beta1 import (
    AbciQueryRequest,
    AbciQueryResponse,
    GetBlockByHeightRequest,
    GetBlockByHeightResponse,
    GetLatestBlockRequest,
    GetLatestBlockResponse,
    GetLatestValidatorSetRequest,
    GetLatestValidatorSetResponse,
    GetNodeInfoRequest,
    GetNodeInfoResponse,
    GetSyncingRequest,
    GetSyncingResponse,
    GetValidatorSetByHeightRequest,
    GetValidatorSetByHeightResponse,
    ServiceStub,
)


class Tendermint:
    def __init__(self, channel: Channel):
        self.query_stub = ServiceStub(channel)

    async def get_node_info(self) -> GetNodeInfoResponse:
        request = GetNodeInfoRequest()
        response = await self.query_stub.get_node_info(request)
        return response

    async def get_syncing(self) -> GetSyncingResponse:
        request = GetSyncingRequest()
        response = await self.query_stub.get_syncing(request)
        return response

    async def get_latest_block(self) -> GetLatestBlockResponse:
        request = GetLatestBlockRequest()
        response = await self.query_stub.get_latest_block(request)
        return response

    async def get_latest_block_height(self) -> int:
        # Extra method to get latest block height
        request = GetLatestBlockRequest()
        response = await self.query_stub.get_latest_block(request)
        return response.sdk_block.header.height

    async def get_block_by_height(self, request: GetBlockByHeightRequest) -> GetBlockByHeightResponse:
        response = await self.query_stub.get_block_by_height(request)
        return response

    async def get_latest_validator_set(
        self, request: GetLatestValidatorSetRequest = GetLatestValidatorSetRequest()
    ) -> GetLatestValidatorSetResponse:
        response = await self.query_stub.get_latest_validator_set(request)
        return response

    async def get_validator_set_by_height(
        self, request: GetValidatorSetByHeightRequest
    ) -> GetValidatorSetByHeightResponse:
        response = await self.query_stub.get_validator_set_by_height(request)
        return response

    async def abci_query(self, request: AbciQueryRequest) -> AbciQueryResponse:
        response = await self.query_stub.abci_query(request)
        return response
