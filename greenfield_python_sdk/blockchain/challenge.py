from grpclib.client import Channel

from greenfield_python_sdk.protos.greenfield.challenge import (
    QueryInturnAttestationSubmitterRequest,
    QueryInturnAttestationSubmitterResponse,
    QueryLatestAttestedChallengesRequest,
    QueryLatestAttestedChallengesResponse,
    QueryParamsRequest,
    QueryParamsResponse,
    QueryStub,
)


class Challenge:
    def __init__(self, channel: Channel):
        self.query_stub = QueryStub(channel)

    async def get_params(self) -> QueryParamsResponse:
        request = QueryParamsRequest()
        response = await self.query_stub.params(request)
        return response

    async def get_latest_attested_challenges(self) -> QueryLatestAttestedChallengesResponse:
        request = QueryLatestAttestedChallengesRequest()
        response = await self.query_stub.latest_attested_challenges(request)
        return response

    async def get_inturn_attestation_submitter(self) -> QueryInturnAttestationSubmitterResponse:
        request = QueryInturnAttestationSubmitterRequest()
        response = await self.query_stub.inturn_attestation_submitter(request)
        return response
