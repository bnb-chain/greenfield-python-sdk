from unittest.mock import MagicMock

import pytest

from greenfield_python_sdk.blockchain.storage import Storage
from greenfield_python_sdk.protos.greenfield.permission import ActionType
from greenfield_python_sdk.protos.greenfield.storage import (
    MsgStub,
    QueryHeadBucketByIdRequest,
    QueryHeadBucketRequest,
    QueryHeadGroupMemberRequest,
    QueryHeadGroupRequest,
    QueryHeadObjectByIdRequest,
    QueryHeadObjectRequest,
    QueryListBucketsRequest,
    QueryListGroupRequest,
    QueryListObjectsByBucketIdRequest,
    QueryListObjectsRequest,
    QueryNftRequest,
    QueryPolicyForAccountRequest,
    QueryPolicyForGroupRequest,
    QueryStub,
    QueryVerifyPermissionRequest,
)

pytestmark = [pytest.mark.unit, pytest.mark.asyncio]


@pytest.fixture
def mock_storage(mock_channel):
    storage = Storage(mock_channel)
    storage.query_stub = MagicMock(spec=QueryStub)
    return storage


async def test_get_params(mock_storage):
    await mock_storage.get_params()
    mock_storage.query_stub.params.assert_called_once()


async def test_get_head_bucket(mock_storage):
    bucket_name = "test_bucket"
    await mock_storage.get_head_bucket(QueryHeadBucketRequest(bucket_name=bucket_name))
    mock_storage.query_stub.head_bucket.assert_called_once()


async def test_get_head_bucket_by_id(mock_storage):
    bucket_id = "test_bucket_id"
    await mock_storage.get_head_bucket_by_id(QueryHeadBucketByIdRequest(bucket_id=bucket_id))
    mock_storage.query_stub.head_bucket_by_id.assert_called_once()


async def test_get_head_bucket_nft(mock_storage):
    token_id = "your_token_id"
    await mock_storage.get_head_bucket_nft(QueryNftRequest(token_id=token_id))
    mock_storage.query_stub.head_bucket_nft.assert_called_once()


async def test_get_head_object(mock_storage):
    bucket_name = "your_bucket_name"
    object_name = "your_object_name"
    await mock_storage.get_head_object(QueryHeadObjectRequest(bucket_name=bucket_name, object_name=object_name))
    mock_storage.query_stub.head_object.assert_called_once()


async def test_get_head_object_by_id(mock_storage):
    object_id = "your_object_id"
    await mock_storage.get_head_object_by_id(QueryHeadObjectByIdRequest(object_id=object_id))
    mock_storage.query_stub.head_object_by_id.assert_called_once()


async def test_get_head_object_nft(mock_storage):
    token_id = "your_token_id"
    await mock_storage.get_head_object_nft(QueryNftRequest(token_id=token_id))
    mock_storage.query_stub.head_object_nft.assert_called_once()


async def test_list_buckets(mock_storage):
    await mock_storage.list_buckets(QueryListBucketsRequest())
    mock_storage.query_stub.list_buckets.assert_called_once()


async def test_list_objects(mock_storage):
    bucket_name = "your_bucket_name"
    await mock_storage.list_objects(QueryListObjectsRequest(bucket_name=bucket_name))
    mock_storage.query_stub.list_objects.assert_called_once()


async def test_list_objects_by_bucket_id(mock_storage):
    bucket_id = "your_bucket_id"
    await mock_storage.list_objects_by_bucket_id(QueryListObjectsByBucketIdRequest(bucket_id=bucket_id))
    mock_storage.query_stub.list_objects_by_bucket_id.assert_called_once()


async def test_get_head_group_nft(mock_storage):
    token_id = "your_token_id"
    await mock_storage.get_head_group_nft(QueryNftRequest(token_id=token_id))
    mock_storage.query_stub.head_group_nft.assert_called_once()


async def test_get_policy_for_account(mock_storage):
    resource = "your_resource"
    principal_address = "your_principal_address"
    await mock_storage.get_policy_for_account(
        QueryPolicyForAccountRequest(resource=resource, principal_address=principal_address)
    )
    mock_storage.query_stub.query_policy_for_account.assert_called_once()


async def test_verify_permission(mock_storage):
    operator = "your_operator"
    bucket_name = "your_bucket_name"
    object_name = "your_object_name"
    action_type = ActionType.ACTION_UPDATE_BUCKET_INFO
    await mock_storage.verify_permission(
        QueryVerifyPermissionRequest(
            operator=operator,
            bucket_name=bucket_name,
            object_name=object_name,
            action_type=action_type,
        )
    )
    mock_storage.query_stub.verify_permission.assert_called_once()


async def test_get_head_group(mock_storage):
    group_owner = "your_group_owner"
    group_name = "your_group_name"
    await mock_storage.get_head_group(QueryHeadGroupRequest(group_owner=group_owner, group_name=group_name))
    mock_storage.query_stub.head_group.assert_called_once()


async def test_list_group(mock_storage):
    group_owner = "your_group_owner"
    await mock_storage.list_group(QueryListGroupRequest(group_owner=group_owner))
    mock_storage.query_stub.list_group.assert_called_once()


async def test_get_head_group_member(mock_storage):
    member = "your_member"
    group_owner = "your_group_owner"
    group_name = "your_group_name"
    await mock_storage.get_head_group_member(
        QueryHeadGroupMemberRequest(member=member, group_owner=group_owner, group_name=group_name)
    )
    mock_storage.query_stub.head_group_member.assert_called_once()


async def test_get_policy_for_group(mock_storage):
    resource = "your_resource"
    principal_group_id = "your_principal_group_id"
    await mock_storage.get_policy_for_group(
        QueryPolicyForGroupRequest(resource=resource, principal_group_id=principal_group_id)
    )
    mock_storage.query_stub.query_policy_for_group.assert_called_once()
