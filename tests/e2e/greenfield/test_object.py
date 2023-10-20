import asyncio
import io
import os
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
from greenfield_python_sdk.models.bucket import CreateBucketOptions
from greenfield_python_sdk.models.object import (
    CreateObjectOptions,
    GetObjectOption,
    ListObjectsOptions,
    PutObjectOptions,
)
from greenfield_python_sdk.models.request import Principal, PutPolicyOption
from greenfield_python_sdk.protos.greenfield.permission import ActionType, Effect, Policy, PrincipalType, Statement
from greenfield_python_sdk.protos.greenfield.sp import QueryStorageProvidersRequest
from greenfield_python_sdk.protos.greenfield.storage import ObjectInfo, VisibilityType
from greenfield_python_sdk.storage_provider.utils import create_example_object

pytestmark = [pytest.mark.asyncio, pytest.mark.e2e]


network_configuration = NetworkConfiguration(**NetworkTestnet().model_dump())
principal_key_manager = KeyManager()

CONTENT = create_example_object()
DOWNLOADING_FILE_DIRECTORY = os.path.dirname(os.path.realpath(__file__)) + "/doc/download_file.txt"
UPLODING_FILE_DIRECTORY = os.path.dirname(os.path.realpath(__file__)) + "/doc/upload_file.txt"


@pytest.mark.requires_config
@pytest.mark.tx
@pytest.mark.slow
@pytest.mark.go_library
async def test_create_object():
    config = get_account_configuration()
    key_manager = KeyManager(private_key=config.private_key)
    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        bucket_name = "".join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(5, 11)))
        object_name = "".join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(5, 11)))

        await client.async_init()
        sp = await client.blockchain_client.sp.get_first_in_service_storage_provider()

        bucket_list = await client.bucket.list_buckets(sp["operator_address"])
        buckets = [bucket.bucket_info.bucket_name for bucket in bucket_list]
        for bucket_name in buckets:
            list_object = await client.object.list_objects(bucket_name, ListObjectsOptions())
            if list_object.key_count > 0:
                for object in list_object.objects:
                    tx_hash = await client.object.delete_object(
                        bucket_name,
                        object.object_name,
                    )
                    assert tx_hash
                    await client.basic.wait_for_tx(hash=tx_hash)

            tx_hash = await client.bucket.delete_bucket(bucket_name)
            assert tx_hash
            await client.basic.wait_for_tx(hash=tx_hash)

        tx_hash = await client.bucket.create_bucket(
            bucket_name,
            primary_sp_address=sp["operator_address"],
            opts=CreateBucketOptions(charged_read_quota=100, visibility=VisibilityType.VISIBILITY_TYPE_PRIVATE),
        )
        assert tx_hash
        assert len(tx_hash) == 64
        assert isinstance(tx_hash, str)
        await client.basic.wait_for_tx(hash=tx_hash)

        tx_hash = await client.object.create_object(
            bucket_name,
            object_name,
            CONTENT,
            opts=CreateObjectOptions(),
        )
        assert tx_hash
        assert len(tx_hash) == 64
        assert isinstance(tx_hash, str)
        await client.basic.wait_for_tx(hash=tx_hash)

        put_object = await client.object.put_object(
            bucket_name,
            object_name,
            CONTENT.getbuffer().nbytes,
            CONTENT.getvalue(),
            opts=PutObjectOptions(),
        )
        assert put_object == "Object added successfully"

        head_object = await client.object.get_object_head(bucket_name, object_name)
        assert head_object
        assert head_object.bucket_name == bucket_name
        assert head_object.object_name == object_name
        assert head_object.owner == key_manager.address
        assert isinstance(head_object, ObjectInfo)

        object_id = await client.object.get_object_head_by_id(head_object.id)
        assert object_id
        assert object_id.bucket_name == bucket_name
        assert object_id.object_name == object_name
        assert isinstance(object_id, ObjectInfo)

        await asyncio.sleep(9)
        info, object = await client.object.get_object(bucket_name, object_name, GetObjectOption())
        assert object
        assert info
        assert info.object_name == object_name
        assert info.content_type == "application/octet-stream"
        assert info.size == 214

        list_object = await client.object.list_objects(bucket_name, ListObjectsOptions())

        assert list_object
        assert list_object.name == bucket_name
        assert list_object.key_count == 1
        assert object_name in list_object.objects[0].object_name

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
@pytest.mark.go_library
async def test_update_object():
    config = get_account_configuration()
    key_manager = KeyManager(private_key=config.private_key)
    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        bucket_name = "".join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(5, 11)))
        object_name = "".join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(5, 11)))

        await client.async_init()
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

        tx_hash = await client.object.create_object(
            bucket_name,
            object_name,
            CONTENT,
            opts=CreateObjectOptions(),
        )
        assert tx_hash
        assert len(tx_hash) == 64
        assert isinstance(tx_hash, str)
        await client.basic.wait_for_tx(hash=tx_hash)

        put_object = await client.object.put_object(
            bucket_name,
            object_name,
            CONTENT.getbuffer().nbytes,
            CONTENT.getvalue(),
            opts=PutObjectOptions(),
        )
        assert put_object == "Object added successfully"

        await asyncio.sleep(5)
        tx_hash = await client.object.update_object_visibility(
            bucket_name,
            object_name,
            visibility=VisibilityType.VISIBILITY_TYPE_PUBLIC_READ,
        )
        assert tx_hash
        assert len(tx_hash) == 64
        assert isinstance(tx_hash, str)
        await client.basic.wait_for_tx(hash=tx_hash)

        permission = await client.object.get_object_permission(
            key_manager.address, bucket_name, object_name, ActionType.ACTION_CREATE_OBJECT
        )
        assert permission
        assert permission == Effect(1).name

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
@pytest.mark.go_library
async def test_put_object_policy():
    config = get_account_configuration()
    key_manager = KeyManager(private_key=config.private_key)
    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        bucket_name = "".join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(5, 11)))
        object_name = "".join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(5, 11)))
        await client.async_init()
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

        tx_hash = await client.object.create_object(
            bucket_name,
            object_name,
            CONTENT,
            opts=CreateObjectOptions(),
        )
        assert tx_hash
        assert len(tx_hash) == 64
        assert isinstance(tx_hash, str)
        await client.basic.wait_for_tx(hash=tx_hash)

        put_object = await client.object.put_object(
            bucket_name,
            object_name,
            CONTENT.getbuffer().nbytes,
            CONTENT.getvalue(),
            opts=PutObjectOptions(),
        )
        assert put_object == "Object added successfully"

        await asyncio.sleep(3)
        statements = [
            Statement(
                effect=Effect.EFFECT_ALLOW,
                actions=[
                    ActionType.ACTION_CREATE_OBJECT,
                    ActionType.ACTION_DELETE_OBJECT,
                ],
            )
        ]
        principal = Principal(type=PrincipalType.PRINCIPAL_TYPE_GNFD_ACCOUNT, value=principal_key_manager.address)

        tx_hash = await client.object.put_object_policy(
            bucket_name,
            object_name,
            principal,
            statements,
            PutPolicyOption(policy_expire_time=datetime.now() + timedelta(weeks=1)),
        )
        assert tx_hash
        assert len(tx_hash) == 64
        assert isinstance(tx_hash, str)
        await client.basic.wait_for_tx(hash=tx_hash)

        head_object = await client.object.get_object_head(bucket_name, object_name)
        assert head_object

        policy = await client.object.get_object_policy(bucket_name, object_name, principal_key_manager.address)
        assert policy
        assert policy.resource_id == head_object.id
        assert isinstance(policy, Policy)

        principal = Principal(type=PrincipalType.PRINCIPAL_TYPE_GNFD_ACCOUNT, value=principal_key_manager.address)
        tx_hash = await client.object.delete_object_policy(bucket_name, object_name, principal)
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
@pytest.mark.go_library
async def test_cancel_creation_object():
    config = get_account_configuration()
    key_manager = KeyManager(private_key=config.private_key)
    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        bucket_name = "".join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(5, 11)))
        object_name = "".join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(5, 11)))
        await client.async_init()
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

        tx_hash = await client.object.create_object(
            bucket_name,
            object_name,
            CONTENT,
            opts=CreateObjectOptions(),
        )
        assert tx_hash
        assert len(tx_hash) == 64
        assert isinstance(tx_hash, str)
        await client.basic.wait_for_tx(hash=tx_hash)

        tx_hash = await client.object.cancel_create_object(
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
@pytest.mark.go_library
async def test_create_folder():
    config = get_account_configuration()
    key_manager = KeyManager(private_key=config.private_key)
    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        bucket_name = "".join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(5, 11)))
        folder_name = "".join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(5, 10))) + "/"
        await client.async_init()
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

        tx_hash = await client.object.create_folder(
            bucket_name,
            folder_name,
            opts=CreateObjectOptions(),
        )
        assert tx_hash
        assert len(tx_hash) == 64
        assert isinstance(tx_hash, str)
        await client.basic.wait_for_tx(hash=tx_hash)

        tx_hash = await client.object.delete_object(
            bucket_name,
            folder_name,
        )
        assert tx_hash
        assert len(tx_hash) == 64
        assert isinstance(tx_hash, str)
        await client.basic.wait_for_tx(hash=tx_hash)

        tx_hash = await client.bucket.delete_bucket(bucket_name)
        assert tx_hash
        await client.basic.wait_for_tx(hash=tx_hash)

        with pytest.raises(Exception):
            await client.object.get_object_head(bucket_name, folder_name)
            await client.bucket.get_bucket_head(bucket_name)


@pytest.mark.requires_config
@pytest.mark.tx
@pytest.mark.slow
@pytest.mark.go_library
async def test_upload_file():
    config = get_account_configuration()
    key_manager = KeyManager(private_key=config.private_key)
    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        file = open(UPLODING_FILE_DIRECTORY, "r")
        upload_data = file.read()
        file.close()
        if os.path.exists(DOWNLOADING_FILE_DIRECTORY):
            os.remove(DOWNLOADING_FILE_DIRECTORY)
        data = io.BytesIO(upload_data.encode("utf-8"))

        bucket_name = "".join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(5, 11)))
        object_name = "".join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(5, 11)))
        await client.async_init()
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

        tx_hash = await client.object.create_object(bucket_name, object_name, reader=data, opts=CreateObjectOptions())
        assert tx_hash
        assert len(tx_hash) == 64
        assert isinstance(tx_hash, str)
        await client.basic.wait_for_tx(hash=tx_hash)

        fput_object = await client.object.fput_object(
            bucket_name, object_name, UPLODING_FILE_DIRECTORY, PutObjectOptions()
        )
        assert fput_object == "Object added successfully"

        await asyncio.sleep(8)
        await client.object.fget_object(bucket_name, object_name, DOWNLOADING_FILE_DIRECTORY, GetObjectOption())
        assert os.path.exists(DOWNLOADING_FILE_DIRECTORY)
        file = open(DOWNLOADING_FILE_DIRECTORY, "r")
        download_data = file.read()
        file.close()
        assert upload_data == download_data

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
