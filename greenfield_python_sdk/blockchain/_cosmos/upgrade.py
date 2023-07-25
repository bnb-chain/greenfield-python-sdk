from grpclib.client import Channel

from greenfield_python_sdk.protos.cosmos.upgrade.v1beta1 import (
    QueryAppliedPlanRequest,
    QueryAppliedPlanResponse,
    QueryCurrentPlanRequest,
    QueryCurrentPlanResponse,
    QueryModuleVersionsRequest,
    QueryModuleVersionsResponse,
    QueryStub,
    QueryUpgradedConsensusStateRequest,
    QueryUpgradedConsensusStateResponse,
)


class Upgrade:
    def __init__(self, channel: Channel):
        self.query_stub = QueryStub(channel)

    async def get_current_plan(self) -> QueryCurrentPlanResponse:
        request = QueryCurrentPlanRequest()
        response = await self.query_stub.current_plan(request)
        return response

    async def get_applied_plan(self, request: QueryAppliedPlanRequest) -> QueryAppliedPlanResponse:
        response = await self.query_stub.applied_plan(request)
        return response

    async def get_upgraded_consensus_state(
        self, request: QueryUpgradedConsensusStateRequest
    ) -> QueryUpgradedConsensusStateResponse:
        response = await self.query_stub.upgraded_consensus_state(request)
        return response

    async def get_module_versions(self, request: QueryModuleVersionsRequest) -> QueryModuleVersionsResponse:
        response = await self.query_stub.module_versions(request)
        return response
