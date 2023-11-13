from betterproto import Casing
from grpclib.client import Channel

from greenfield_python_sdk.protos.greenfield.sp import (
    QueryGlobalSpStorePriceByTimeRequest,
    QueryGlobalSpStorePriceByTimeResponse,
    QueryParamsRequest,
    QueryParamsResponse,
    QuerySpStoragePriceRequest,
    QuerySpStoragePriceResponse,
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

    async def get_storage_provider(self, request: QueryStorageProviderRequest) -> QueryStorageProviderResponse:
        response = await self.query_stub.storage_provider(request)
        return response

    async def get_sp_storage_price(self, request: QuerySpStoragePriceRequest) -> QuerySpStoragePriceResponse:
        response = await self.query_stub.query_sp_storage_price(request)
        return response

    async def get_first_in_service_storage_provider(self):
        response = await self.get_storage_providers()
        if response.sps is None:
            raise Exception("Storage providers not found")

        sps = response.to_pydict(casing=Casing.SNAKE)["sps"]
        for sp in sps:
            if sp.get("status", 0) == 0:
                return sp

        raise Exception("No Storage Provider in service")

    async def get_global_sp_store_price_by_time(
        self, request: QueryGlobalSpStorePriceByTimeRequest
    ) -> QueryGlobalSpStorePriceByTimeResponse:
        response = await self.query_stub.query_global_sp_store_price_by_time(request)
        return response
