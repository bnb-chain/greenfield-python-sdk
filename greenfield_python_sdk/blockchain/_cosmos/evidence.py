from grpclib.client import Channel

from greenfield_python_sdk.protos.cosmos.evidence.v1beta1 import (
    QueryAllEvidenceRequest,
    QueryAllEvidenceResponse,
    QueryEvidenceRequest,
    QueryEvidenceResponse,
    QueryStub,
)


class Evidence:
    def __init__(self, channel: Channel):
        self.query_stub = QueryStub(channel)

    async def get_evidence(self, request: QueryEvidenceRequest) -> QueryEvidenceResponse:
        response = await self.query_stub.evidence(request)
        return response

    async def all_evidence(
        self, request: QueryAllEvidenceRequest = QueryAllEvidenceRequest()
    ) -> QueryAllEvidenceResponse:
        response = await self.query_stub.all_evidence(request)
        return response
