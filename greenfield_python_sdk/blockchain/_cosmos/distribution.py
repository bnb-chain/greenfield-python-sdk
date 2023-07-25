from grpclib.client import Channel

from greenfield_python_sdk.protos.cosmos.distribution.v1beta1 import (
    QueryCommunityPoolRequest,
    QueryCommunityPoolResponse,
    QueryDelegationRewardsRequest,
    QueryDelegationRewardsResponse,
    QueryDelegationTotalRewardsRequest,
    QueryDelegationTotalRewardsResponse,
    QueryDelegatorValidatorsRequest,
    QueryDelegatorValidatorsResponse,
    QueryDelegatorWithdrawAddressRequest,
    QueryDelegatorWithdrawAddressResponse,
    QueryParamsRequest,
    QueryParamsResponse,
    QueryStub,
    QueryValidatorCommissionRequest,
    QueryValidatorCommissionResponse,
    QueryValidatorOutstandingRewardsRequest,
    QueryValidatorOutstandingRewardsResponse,
    QueryValidatorSlashesRequest,
    QueryValidatorSlashesResponse,
)


class Distribution:
    def __init__(self, channel: Channel):
        self.query_stub = QueryStub(channel)

    async def params(self, request: QueryParamsRequest) -> QueryParamsResponse:
        response = await self.query_stub.params(request)
        return response

    async def validator_outstanding_rewards(
        self, request: QueryValidatorOutstandingRewardsRequest
    ) -> QueryValidatorOutstandingRewardsResponse:
        response = await self.query_stub.validator_outstanding_rewards(request)
        return response

    async def validator_commission(self, request: QueryValidatorCommissionRequest) -> QueryValidatorCommissionResponse:
        response = await self.query_stub.validator_commission(request)
        return response

    async def validator_slashes(self, request: QueryValidatorSlashesRequest) -> QueryValidatorSlashesResponse:
        response = await self.query_stub.validator_slashes(request)
        return response

    async def delegation_rewards(self, request: QueryDelegationRewardsRequest) -> QueryDelegationRewardsResponse:
        response = await self.query_stub.delegation_rewards(request)
        return response

    async def delegation_total_rewards(
        self, request: QueryDelegationTotalRewardsRequest
    ) -> QueryDelegationTotalRewardsResponse:
        response = await self.query_stub.delegation_total_rewards(request)
        return response

    async def delegator_validators(self, request: QueryDelegatorValidatorsRequest) -> QueryDelegatorValidatorsResponse:
        response = await self.query_stub.delegator_validators(request)
        return response

    async def delegator_withdraw_address(
        self, request: QueryDelegatorWithdrawAddressRequest
    ) -> QueryDelegatorWithdrawAddressResponse:
        response = await self.query_stub.delegator_withdraw_address(request)
        return response

    async def community_pool(self) -> QueryCommunityPoolResponse:
        request = QueryCommunityPoolRequest()
        response = await self.query_stub.community_pool(request)
        return response
