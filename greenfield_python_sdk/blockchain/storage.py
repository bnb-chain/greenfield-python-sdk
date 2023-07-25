from grpclib.client import Channel

from greenfield_python_sdk.protos.greenfield.permission import ActionType
from greenfield_python_sdk.protos.greenfield.storage import (
    QueryBucketNftResponse,
    QueryGroupNftResponse,
    QueryHeadBucketByIdRequest,
    QueryHeadBucketRequest,
    QueryHeadBucketResponse,
    QueryHeadGroupMemberRequest,
    QueryHeadGroupMemberResponse,
    QueryHeadGroupRequest,
    QueryHeadGroupResponse,
    QueryHeadObjectByIdRequest,
    QueryHeadObjectRequest,
    QueryHeadObjectResponse,
    QueryListBucketsRequest,
    QueryListBucketsResponse,
    QueryListGroupRequest,
    QueryListGroupResponse,
    QueryListObjectsByBucketIdRequest,
    QueryListObjectsRequest,
    QueryListObjectsResponse,
    QueryNftRequest,
    QueryObjectNftResponse,
    QueryParamsRequest,
    QueryParamsResponse,
    QueryPolicyForAccountRequest,
    QueryPolicyForAccountResponse,
    QueryPolicyForGroupRequest,
    QueryPolicyForGroupResponse,
    QueryStub,
    QueryVerifyPermissionRequest,
    QueryVerifyPermissionResponse,
)


class Storage:
    def __init__(self, channel: Channel):
        self.query_stub = QueryStub(channel)

    async def get_params(self) -> QueryParamsResponse:
        request = QueryParamsRequest()
        response = await self.query_stub.params(request)
        return response

    async def get_head_bucket(self, request=QueryHeadBucketRequest) -> QueryHeadBucketResponse:
        response = await self.query_stub.head_bucket(request)
        return response

    async def get_head_bucket_by_id(self, request: QueryHeadBucketByIdRequest) -> QueryHeadBucketResponse:
        response = await self.query_stub.head_bucket_by_id(request)
        return response

    async def get_head_bucket_nft(self, request: QueryNftRequest) -> QueryBucketNftResponse:
        response = await self.query_stub.head_bucket_nft(request)
        return response

    async def get_head_object(self, request: QueryHeadObjectRequest) -> QueryHeadObjectResponse:
        response = await self.query_stub.head_object(request)
        return response

    async def get_head_object_by_id(self, request: QueryHeadObjectByIdRequest) -> QueryHeadObjectResponse:
        response = await self.query_stub.head_object_by_id(request)
        return response

    async def get_head_object_nft(self, request: QueryNftRequest) -> QueryObjectNftResponse:
        response = await self.query_stub.head_object_nft(request)
        return response

    async def list_buckets(
        self, request: QueryListBucketsRequest = QueryListBucketsRequest()
    ) -> QueryListBucketsResponse:
        response = await self.query_stub.list_buckets(request)
        return response

    async def list_objects(self, request: QueryListObjectsRequest) -> QueryListObjectsResponse:
        response = await self.query_stub.list_objects(request)
        return response

    async def list_objects_by_bucket_id(self, request: QueryListObjectsByBucketIdRequest) -> QueryListObjectsResponse:
        response = await self.query_stub.list_objects_by_bucket_id(request)
        return response

    async def get_head_group_nft(self, request: QueryNftRequest) -> QueryGroupNftResponse:
        response = await self.query_stub.head_group_nft(request)
        return response

    async def get_policy_for_account(self, request: QueryPolicyForAccountRequest) -> QueryPolicyForAccountResponse:
        response = await self.query_stub.query_policy_for_account(request)
        return response

    async def verify_permission(self, request: QueryVerifyPermissionRequest) -> QueryVerifyPermissionResponse:
        response = await self.query_stub.verify_permission(request)
        return response

    async def get_head_group(self, request: QueryHeadGroupRequest) -> QueryHeadGroupResponse:
        response = await self.query_stub.head_group(request)
        return response

    async def list_group(self, request: QueryListGroupRequest) -> QueryListGroupResponse:
        response = await self.query_stub.list_group(request)
        return response

    async def get_head_group_member(self, request: QueryHeadGroupMemberRequest) -> QueryHeadGroupMemberResponse:
        response = await self.query_stub.head_group_member(request)
        return response

    async def get_policy_for_group(self, request: QueryPolicyForGroupRequest) -> QueryPolicyForGroupResponse:
        response = await self.query_stub.query_policy_for_group(request)
        return response
