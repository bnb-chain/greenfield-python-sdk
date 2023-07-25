from grpclib.client import Channel

from greenfield_python_sdk.protos.cosmos.staking.v1beta1 import (
    QueryDelegationRequest,
    QueryDelegationResponse,
    QueryDelegatorDelegationsRequest,
    QueryDelegatorDelegationsResponse,
    QueryDelegatorUnbondingDelegationsRequest,
    QueryDelegatorUnbondingDelegationsResponse,
    QueryDelegatorValidatorRequest,
    QueryDelegatorValidatorResponse,
    QueryDelegatorValidatorsRequest,
    QueryDelegatorValidatorsResponse,
    QueryHistoricalInfoRequest,
    QueryHistoricalInfoResponse,
    QueryParamsRequest,
    QueryParamsResponse,
    QueryPoolRequest,
    QueryPoolResponse,
    QueryRedelegationsRequest,
    QueryRedelegationsResponse,
    QueryStub,
    QueryUnbondingDelegationRequest,
    QueryUnbondingDelegationResponse,
    QueryValidatorDelegationsRequest,
    QueryValidatorDelegationsResponse,
    QueryValidatorRequest,
    QueryValidatorResponse,
    QueryValidatorsRequest,
    QueryValidatorsResponse,
    QueryValidatorUnbondingDelegationsRequest,
    QueryValidatorUnbondingDelegationsResponse,
)


class Staking:
    def __init__(self, channel: Channel):
        self.query_stub = QueryStub(channel)

    async def get_params(self) -> QueryParamsResponse:
        request = QueryParamsRequest()
        response = await self.query_stub.params(request)
        return response

    async def get_pool(self) -> QueryPoolResponse:
        request = QueryPoolRequest()
        response = await self.query_stub.pool(request)
        return response

    async def get_historical_info(self, request: QueryHistoricalInfoRequest) -> QueryHistoricalInfoResponse:
        response = await self.query_stub.historical_info(request)
        return response

    async def get_delegator_validators(
        self, request: QueryDelegatorValidatorsRequest
    ) -> QueryDelegatorValidatorsResponse:
        response = await self.query_stub.delegator_validators(request)
        return response

    async def get_delegator_validator(self, request: QueryDelegatorValidatorRequest) -> QueryDelegatorValidatorResponse:
        response = await self.query_stub.delegator_validator(request)
        return response

    async def get_redelegations(self, request: QueryRedelegationsRequest) -> QueryRedelegationsResponse:
        response = await self.query_stub.redelegations(request)
        return response

    async def get_delegator_unbonding_delegations(
        self, request: QueryDelegatorUnbondingDelegationsRequest
    ) -> QueryDelegatorUnbondingDelegationsResponse:
        response = await self.query_stub.delegator_unbonding_delegations(request)
        return response

    async def get_delegator_delegations(
        self, request: QueryDelegatorDelegationsRequest
    ) -> QueryDelegatorDelegationsResponse:
        response = await self.query_stub.delegator_delegations(request)
        return response

    async def get_unbonding_delegation(
        self, request: QueryUnbondingDelegationRequest
    ) -> QueryUnbondingDelegationResponse:
        response = await self.query_stub.unbonding_delegation(request)
        return response

    async def get_delegation(self, request: QueryDelegationRequest) -> QueryDelegationResponse:
        response = await self.query_stub.delegation(request)
        return response

    async def get_validator_unbonding_delegations(
        self, request: QueryValidatorUnbondingDelegationsRequest
    ) -> QueryValidatorUnbondingDelegationsResponse:
        response = await self.query_stub.validator_unbonding_delegations(request)
        return response

    async def get_validator_delegations(
        self, request: QueryValidatorDelegationsRequest
    ) -> QueryValidatorDelegationsResponse:
        response = await self.query_stub.validator_delegations(request)
        return response

    async def get_validators(self, request: QueryValidatorsRequest) -> QueryValidatorsResponse:
        response = await self.query_stub.validators(request)
        return response

    async def get_validator(self, request: QueryValidatorRequest) -> QueryValidatorResponse:
        response = await self.query_stub.validator(request)
        return response
