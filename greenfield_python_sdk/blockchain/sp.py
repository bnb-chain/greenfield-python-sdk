from grpclib.client import Channel

from greenfield_python_sdk.protos.greenfield.sp import (
    QueryGetSecondarySpStorePriceByTimeRequest,
    QueryGetSecondarySpStorePriceByTimeResponse,
    QueryGetSpStoragePriceByTimeRequest,
    QueryGetSpStoragePriceByTimeResponse,
    QueryParamsRequest,
    QueryParamsResponse,
    QueryStorageProviderRequest,
    QueryStorageProviderResponse,
    QueryStorageProvidersRequest,
    QueryStorageProvidersResponse,
    QueryStub,
)


class Sp:
    def __init__(self, channel: Channel):
        self.query_stub = QueryStub(channel)

    async def get_params(self) -> QueryParamsResponse:
        request = QueryParamsRequest()
        response = await self.query_stub.params(request)
        return response

    async def get_storage_providers(
        self, request: QueryStorageProvidersRequest = QueryStorageProvidersRequest()
    ) -> QueryStorageProvidersResponse:
        response = await self.query_stub.storage_providers(request)
        return response

    async def get_sp_storage_price_by_time(
        self, request: QueryGetSpStoragePriceByTimeRequest
    ) -> QueryGetSpStoragePriceByTimeResponse:
        response = await self.query_stub.query_get_sp_storage_price_by_time(request)
        return response

    async def get_secondary_sp_store_price_by_time(
        self, request: QueryGetSecondarySpStorePriceByTimeRequest
    ) -> QueryGetSecondarySpStorePriceByTimeResponse:
        response = await self.query_stub.query_get_secondary_sp_store_price_by_time(request)
        return response

    async def get_storage_provider(self, request: QueryStorageProviderRequest) -> QueryStorageProviderResponse:
        response = await self.query_stub.storage_provider(request)
        return response
