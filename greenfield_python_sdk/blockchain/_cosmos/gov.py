from grpclib.client import Channel

from greenfield_python_sdk.protos.cosmos.gov.v1 import (
    QueryDepositRequest,
    QueryDepositResponse,
    QueryDepositsRequest,
    QueryDepositsResponse,
    QueryParamsRequest,
    QueryParamsResponse,
    QueryProposalRequest,
    QueryProposalResponse,
    QueryProposalsRequest,
    QueryProposalsResponse,
    QueryStub,
    QueryTallyResultRequest,
    QueryTallyResultResponse,
    QueryVoteRequest,
    QueryVoteResponse,
    QueryVotesRequest,
    QueryVotesResponse,
)


class Gov:
    def __init__(self, channel: Channel):
        self.query_stub = QueryStub(channel)

    async def get_proposal(self, query_proposal_request: QueryProposalRequest) -> QueryProposalResponse:
        response = await self.query_stub.proposal(query_proposal_request)
        return response

    async def get_proposals(self, request: QueryProposalsRequest) -> QueryProposalsResponse:
        response = await self.query_stub.proposals(request)
        return response

    async def get_vote(self, request: QueryVoteRequest) -> QueryVoteResponse:
        response = await self.query_stub.vote(request)
        return response

    async def get_votes(self, request: QueryVotesRequest) -> QueryVotesResponse:
        response = await self.query_stub.votes(request)
        return response

    async def get_params(self, request: QueryParamsRequest) -> QueryParamsResponse:
        response = await self.query_stub.params(request)
        return response

    async def get_deposit(self, request: QueryDepositRequest) -> QueryDepositResponse:
        response = await self.query_stub.deposit(request)
        return response

    async def get_deposits(self, request: QueryDepositsRequest) -> QueryDepositsResponse:
        response = await self.query_stub.deposits(request)
        return response

    async def get_tally_result(self, request: QueryTallyResultRequest) -> QueryTallyResultResponse:
        response = await self.query_stub.tally_result(request)
        return response
