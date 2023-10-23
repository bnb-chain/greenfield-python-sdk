import asyncio
import random
import string
from datetime import datetime, timedelta

import pytest

from greenfield_python_sdk import (
    GreenfieldClient,
    KeyManager,
    NetworkConfiguration,
    NetworkTestnet,
    get_account_configuration,
)
from greenfield_python_sdk.greenfield.account import Coin
from greenfield_python_sdk.models.bucket import CreateBucketOptions
from greenfield_python_sdk.models.group import CreateGroupOptions, ListGroupsOptions
from greenfield_python_sdk.models.object import CreateObjectOptions, PutObjectOptions
from greenfield_python_sdk.models.request import Principal, PutPolicyOption
from greenfield_python_sdk.protos.greenfield.permission import ActionType, Effect, PrincipalType, Statement
from greenfield_python_sdk.protos.greenfield.sp import QueryStorageProvidersRequest
from greenfield_python_sdk.protos.greenfield.storage import VisibilityType
from greenfield_python_sdk.storage_provider.utils import create_example_object

pytestmark = [pytest.mark.asyncio, pytest.mark.e2e]


network_configuration = NetworkConfiguration(**NetworkTestnet().model_dump())
group_key_manager = KeyManager()


@pytest.mark.requires_config
@pytest.mark.tx
@pytest.mark.slow
async def test_create_group():
    config = get_account_configuration()
    key_manager = KeyManager(private_key=config.private_key)
    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        group_name = "".join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(5, 11)))
        await client.async_init()

        tx_hash = await client.group.create_group(
            group_name=group_name, opts=CreateGroupOptions(init_group_members=[key_manager.address])
        )
        assert tx_hash
        assert len(tx_hash) == 64
        assert isinstance(tx_hash, str)
        await client.basic.wait_for_tx(hash=tx_hash)

        group_head = await client.group.get_group_head(group_name=group_name, group_owner=key_manager.address)
        assert group_head.group_name == group_name
        assert group_head.owner == key_manager.address

        tx_hash = await client.group.delete_group(group_name=group_name)
        assert tx_hash
        assert len(tx_hash) == 64
        assert isinstance(tx_hash, str)
        await client.basic.wait_for_tx(hash=tx_hash)


@pytest.mark.requires_config
@pytest.mark.tx
@pytest.mark.slow
async def test_add_group_members():
    config = get_account_configuration()
    key_manager = KeyManager(private_key=config.private_key)
    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        group_name = "".join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(5, 11)))
        await client.async_init()

        tx_hash = await client.group.create_group(group_name=group_name, opts=CreateGroupOptions())
        assert tx_hash
        assert len(tx_hash) == 64
        assert isinstance(tx_hash, str)
        await client.basic.wait_for_tx(hash=tx_hash)

        tx_hash = await client.group.update_group_member(
            group_name=group_name,
            group_owner=key_manager.address,
            add_addresses=[key_manager.address],
            remove_addresses=[],
        )
        assert tx_hash
        assert len(tx_hash) == 64
        assert isinstance(tx_hash, str)
        await client.basic.wait_for_tx(hash=tx_hash)

        group_member_head = await client.group.get_group_member_head(
            group_name=group_name, group_owner=key_manager.address, head_member=key_manager.address
        )
        assert group_member_head == True

        tx_hash = await client.group.leave_group(group_name=group_name, group_owner=key_manager.address)
        assert tx_hash
        assert len(tx_hash) == 64
        assert isinstance(tx_hash, str)
        await client.basic.wait_for_tx(hash=tx_hash)

        tx_hash = await client.group.delete_group(group_name=group_name)
        assert tx_hash
        assert len(tx_hash) == 64
        assert isinstance(tx_hash, str)
        await client.basic.wait_for_tx(hash=tx_hash)


@pytest.mark.requires_config
@pytest.mark.tx
@pytest.mark.slow
@pytest.mark.go_library
async def test_policy_group():
    config = get_account_configuration()
    key_manager = KeyManager(private_key=config.private_key)
    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        group_name = "".join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(5, 11)))
        bucket_name = "".join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(5, 11)))
        object_name = "".join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(5, 11)))
        content = create_example_object()
        await client.async_init()

        tx_hash = await client.group.create_group(
            group_name=group_name, opts=CreateGroupOptions(init_group_members=[key_manager.address])
        )
        assert tx_hash
        assert len(tx_hash) == 64
        assert isinstance(tx_hash, str)
        await client.basic.wait_for_tx(hash=tx_hash)

        sps = (await client.blockchain_client.sp.get_storage_providers(QueryStorageProvidersRequest())).sps
        tx_hash = await client.bucket.create_bucket(
            bucket_name,
            primary_sp_address=sps[0].operator_address,
            opts=CreateBucketOptions(charged_read_quota=100, visibility=VisibilityType.VISIBILITY_TYPE_PRIVATE),
        )
        assert tx_hash
        assert len(tx_hash) == 64
        assert isinstance(tx_hash, str)
        await client.basic.wait_for_tx(hash=tx_hash)

        group_head = await client.group.get_group_head(group_name=group_name, group_owner=key_manager.address)
        assert group_head.group_name == group_name
        assert group_head.owner == key_manager.address

        statements = [
            Statement(
                effect=Effect.EFFECT_ALLOW,
                actions=[
                    ActionType.ACTION_UPDATE_BUCKET_INFO,
                    ActionType.ACTION_DELETE_BUCKET,
                ],
                # resources=[f"grn:b::{bucket_name}"],
            )
        ]
        principal = Principal(type=PrincipalType.PRINCIPAL_TYPE_GNFD_GROUP, value=group_head.id)

        tx_hash = await client.bucket.put_bucket_policy(bucket_name, principal, statements)
        assert tx_hash
        assert len(tx_hash) == 64
        assert isinstance(tx_hash, str)
        await client.basic.wait_for_tx(hash=tx_hash)

        bucket_policy_of_group = await client.group.get_bucket_policy_of_group(
            bucket_name=bucket_name, group_id=group_head.id
        )
        assert bucket_policy_of_group
        assert bucket_policy_of_group.resource_type == "BUCKET"
        assert bucket_policy_of_group.statements[0].effect == "ALLOW"
        assert bucket_policy_of_group.statements[0].actions[0] == "ACTION_UPDATE_BUCKET_INFO"
        assert bucket_policy_of_group.statements[0].actions[1] == "ACTION_DELETE_BUCKET"

        tx_hash = await client.object.create_object(
            bucket_name, object_name, reader=content, opts=CreateObjectOptions()
        )
        assert tx_hash
        assert len(tx_hash) == 64
        assert isinstance(tx_hash, str)
        await client.basic.wait_for_tx(hash=tx_hash)

        put_object = await client.object.put_object(
            bucket_name,
            object_name,
            content.getbuffer().nbytes,
            content.getvalue(),
            opts=PutObjectOptions(),
        )
        assert put_object == "Object added successfully"

        await asyncio.sleep(4)
        statements = [
            Statement(
                effect=Effect.EFFECT_ALLOW,
                actions=[
                    ActionType.ACTION_CREATE_OBJECT,
                    ActionType.ACTION_DELETE_OBJECT,
                ],
            )
        ]
        principal = Principal(type=PrincipalType.PRINCIPAL_TYPE_GNFD_GROUP, value=group_head.id)

        tx_hash = await client.object.put_object_policy(bucket_name, object_name, principal, statements)
        assert tx_hash
        assert len(tx_hash) == 64
        assert isinstance(tx_hash, str)
        await client.basic.wait_for_tx(hash=tx_hash)

        object_policy_of_group = await client.group.get_object_policy_of_group(
            bucket_name=bucket_name, object_name=object_name, group_id=group_head.id
        )
        assert object_policy_of_group
        assert object_policy_of_group.resource_type == "OBJECT"
        assert object_policy_of_group.statements[0].effect == "ALLOW"
        assert object_policy_of_group.statements[0].actions[0] == "ACTION_CREATE_OBJECT"
        assert object_policy_of_group.statements[0].actions[1] == "ACTION_DELETE_OBJECT"

        await asyncio.sleep(2)
        statements = [
            Statement(
                effect=Effect.EFFECT_ALLOW,
                actions=[
                    ActionType.ACTION_UPDATE_GROUP_MEMBER,
                    ActionType.ACTION_DELETE_GROUP,
                ],
            )
        ]

        tx_hash = await client.group.put_group_policy(
            group_name=group_name,
            principal_addr=group_key_manager.address,
            statements=statements,
            opts=PutPolicyOption(policy_expire_time=datetime.now() + timedelta(weeks=1)),
        )
        assert tx_hash
        assert len(tx_hash) == 64
        assert isinstance(tx_hash, str)
        await client.basic.wait_for_tx(hash=tx_hash)

        get_group_policy = await client.group.get_group_policy(
            group_name=group_name,
            principal_addr=group_key_manager.address,
        )
        assert get_group_policy
        assert get_group_policy.resource_type == "GROUP"
        assert get_group_policy.statements[0].effect == "ALLOW"
        assert get_group_policy.statements[0].actions[0] == "ACTION_UPDATE_GROUP_MEMBER"
        assert get_group_policy.statements[0].actions[1] == "ACTION_DELETE_GROUP"

        tx_hash = await client.group.delete_group_policy(
            group_name=group_name,
            principal_addr=group_key_manager.address,
        )
        assert tx_hash
        assert len(tx_hash) == 64
        assert isinstance(tx_hash, str)
        await client.basic.wait_for_tx(hash=tx_hash)

        tx_hash = await client.object.delete_object(
            bucket_name,
            object_name,
        )
        assert tx_hash
        assert len(tx_hash) == 64
        assert isinstance(tx_hash, str)
        await client.basic.wait_for_tx(hash=tx_hash)

        tx_hash = await client.bucket.delete_bucket(bucket_name)
        assert tx_hash
        await client.basic.wait_for_tx(hash=tx_hash)

        with pytest.raises(Exception):
            await client.object.get_object_head(bucket_name, object_name)
            await client.bucket.get_bucket_head(bucket_name)


@pytest.mark.requires_config
@pytest.mark.tx
@pytest.mark.slow
async def test_list_group():
    config = get_account_configuration()
    key_manager = KeyManager(private_key=config.private_key)
    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        await client.async_init()

        tracker = "".join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(4, 5)))
        prefix = f"test_{tracker}"
        group_name1 = prefix + "-1"
        group_name2 = prefix + "-2"
        group_name3 = prefix + "-3"

        tx_hash = await client.group.create_group(
            group_name=group_name1, opts=CreateGroupOptions(init_group_members=[key_manager.address])
        )
        assert tx_hash
        assert len(tx_hash) == 64
        assert isinstance(tx_hash, str)
        await client.basic.wait_for_tx(hash=tx_hash)

        tx_hash = await client.group.create_group(
            group_name=group_name2, opts=CreateGroupOptions(init_group_members=[key_manager.address])
        )
        assert tx_hash
        assert len(tx_hash) == 64
        assert isinstance(tx_hash, str)
        await client.basic.wait_for_tx(hash=tx_hash)

        tx_hash = await client.group.create_group(
            group_name=group_name3, opts=CreateGroupOptions(init_group_members=[key_manager.address])
        )
        assert tx_hash
        assert len(tx_hash) == 64
        assert isinstance(tx_hash, str)
        await client.basic.wait_for_tx(hash=tx_hash)

        await asyncio.sleep(5)

        list_groups = await client.group.list_group(
            tracker, "_", ListGroupsOptions(source_type="SOURCE_TYPE_ORIGIN", limit=5)
        )

        assert list_groups
        assert len(list_groups) == 3
        assert list_groups[0]["group"]["group_name"] == group_name1
        assert list_groups[1]["group"]["group_name"] == group_name2
        assert list_groups[2]["group"]["group_name"] == group_name3

        tx_hash = await client.group.delete_group(group_name=group_name1)
        assert tx_hash
        assert len(tx_hash) == 64
        assert isinstance(tx_hash, str)
        await client.basic.wait_for_tx(hash=tx_hash)

        tx_hash = await client.group.delete_group(group_name=group_name2)
        assert tx_hash
        assert len(tx_hash) == 64
        assert isinstance(tx_hash, str)
        await client.basic.wait_for_tx(hash=tx_hash)

        tx_hash = await client.group.delete_group(group_name=group_name3)
        assert tx_hash
        assert len(tx_hash) == 64
        assert isinstance(tx_hash, str)
        await client.basic.wait_for_tx(hash=tx_hash)
