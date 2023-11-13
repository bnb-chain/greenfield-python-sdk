from grpclib.client import Channel

from greenfield_python_sdk.protos.greenfield.virtualgroup import (
    QueryGlobalVirtualGroupFamilyRequest,
    QueryGlobalVirtualGroupFamilyResponse,
    QueryStub,
)


class VirtualGroup:
    def __init__(self, channel: Channel):
        self.query_stub = QueryStub(channel)

    async def global_virtual_group_family(
        self, request=QueryGlobalVirtualGroupFamilyRequest
    ) -> QueryGlobalVirtualGroupFamilyResponse:
        return await self.query_stub.global_virtual_group_family(request)
