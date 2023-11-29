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
from greenfield_python_sdk.models.bucket import (
    CreateBucketOptions,
    EndPointOptions,
    GetBucketMeta,
    ListBucketInfo,
    ListBucketReadRecord,
    ListBucketsByBucketIDResponse,
    ListBucketsByPaymentAccountOptions,
    ListBucketsByPaymentAccountResponse,
    ListReadRecordOptions,
    MigrateBucketOptions,
    ReadQuota,
    UpdateBucketOptions,
    VisibilityType,
)
from greenfield_python_sdk.models.request import PutPolicyOption
from greenfield_python_sdk.protos.greenfield.permission import (
    ActionType,
    Effect,
    Policy,
    Principal,
    PrincipalType,
    Statement,
)
from greenfield_python_sdk.protos.greenfield.sp import StorageProvider as SpStorageProvider
from greenfield_python_sdk.protos.greenfield.storage import BucketInfo

pytestmark = [pytest.mark.asyncio, pytest.mark.e2e]


# Initialize the configuration, key manager
network_configuration = NetworkConfiguration(**NetworkTestnet().model_dump())
principal_key_manager = KeyManager()


@pytest.mark.requires_config
@pytest.mark.tx
@pytest.mark.slow
async def test_create_bucket():
    config = get_account_configuration()
    key_manager = KeyManager(private_key=config.private_key)
    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        bucket_name = "".join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(5, 11)))
        await client.async_init()

        sp = (await client.blockchain_client.get_active_sps())[0]
        tx_hash = await client.bucket.create_bucket(
            bucket_name,
            primary_sp_address=sp["operator_address"],
            opts=CreateBucketOptions(charged_read_quota=100, visibility=VisibilityType.VISIBILITY_TYPE_PRIVATE),
        )
        assert tx_hash
        assert len(tx_hash) == 64
        assert isinstance(tx_hash, str)
        await client.basic.wait_for_tx(hash=tx_hash)

        head_bucket = await client.bucket.get_bucket_head(bucket_name)
        assert head_bucket
        assert head_bucket.bucket_name == bucket_name
        assert head_bucket.owner == key_manager.address
        assert isinstance(head_bucket, BucketInfo)

        bucket_id = await client.bucket.get_head_bucket_by_id(head_bucket.id)
        assert bucket_id
        assert bucket_id.bucket_name == bucket_name
        assert isinstance(bucket_id, BucketInfo)

        list_bucket = await client.bucket.list_buckets_by_bucket_id(
            [head_bucket.id], EndPointOptions(sp_address=sp["operator_address"])
        )
        assert list_bucket
        assert list_bucket[0].bucket_info.bucket_name == bucket_name
        assert isinstance(list_bucket, list)
        assert isinstance(list_bucket[0], ListBucketsByBucketIDResponse)

        await asyncio.sleep(3)
        sp = await client.bucket.storage_provider_by_bucket(bucket_name)
        list_buckets = await client.bucket.list_buckets(sp)
        assert list_buckets
        names = [bucket_info.bucket_info.bucket_name for bucket_info in list_buckets]
        assert bucket_name in names
        assert isinstance(list_buckets[0], ListBucketInfo)

        tx_hash = await client.bucket.delete_bucket(bucket_name)
        assert tx_hash
        await client.basic.wait_for_tx(hash=tx_hash)

        # Check that the bucket is deleted
        with pytest.raises(Exception):
            await client.bucket.get_bucket_head(bucket_name)


@pytest.mark.requires_config
@pytest.mark.tx
@pytest.mark.slow
async def test_update_bucket():
    config = get_account_configuration()
    key_manager = KeyManager(private_key=config.private_key)
    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        await client.async_init()
        bucket_name = "".join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(5, 11)))
        sp = (await client.blockchain_client.get_active_sps())[0]
        tx_hash = await client.bucket.create_bucket(
            bucket_name,
            primary_sp_address=sp["operator_address"],
            opts=CreateBucketOptions(charged_read_quota=100, visibility=VisibilityType.VISIBILITY_TYPE_PRIVATE),
        )
        assert tx_hash
        assert len(tx_hash) == 64
        assert isinstance(tx_hash, str)
        await client.basic.wait_for_tx(hash=tx_hash)

        tx_hash = await client.bucket.update_bucket_visibility(
            bucket_name, visibility=VisibilityType.VISIBILITY_TYPE_PUBLIC_READ
        )
        assert tx_hash
        assert len(tx_hash) == 64
        assert isinstance(tx_hash, str)
        await client.basic.wait_for_tx(hash=tx_hash)

        tx_hash = await client.bucket.update_bucket_info(
            bucket_name,
            opts=UpdateBucketOptions(charged_read_quota=1000, visibility=VisibilityType.VISIBILITY_TYPE_PRIVATE),
        )
        assert tx_hash
        assert len(tx_hash) == 64
        assert isinstance(tx_hash, str)
        await client.basic.wait_for_tx(hash=tx_hash)

        update_time = await client.bucket.get_quota_update_time(bucket_name)
        assert update_time
        assert isinstance(update_time, int)

        account = await client.account.get_account(address=client.key_manager.address)
        client.key_manager.account.next_sequence = account.sequence
        tx_hash = await client.bucket.update_bucket_payment_addr(bucket_name, payment_addr=key_manager.address)
        assert tx_hash
        assert len(tx_hash) == 64
        assert isinstance(tx_hash, str)
        await client.basic.wait_for_tx(hash=tx_hash)

        tx_hash = await client.bucket.delete_bucket(bucket_name)
        assert tx_hash
        await client.basic.wait_for_tx(hash=tx_hash)

        # Check that the bucket is deleted
        with pytest.raises(Exception):
            await client.bucket.get_bucket_head(bucket_name)


@pytest.mark.requires_config
@pytest.mark.tx
@pytest.mark.slow
async def test_put_bucket_policy():
    config = get_account_configuration()
    key_manager = KeyManager(private_key=config.private_key)
    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        await client.async_init()

        bucket_name = "".join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(5, 11)))
        sp = (await client.blockchain_client.get_active_sps())[0]
        tx_hash = await client.bucket.create_bucket(
            bucket_name,
            primary_sp_address=sp["operator_address"],
            opts=CreateBucketOptions(charged_read_quota=100, visibility=VisibilityType.VISIBILITY_TYPE_PRIVATE),
        )
        assert tx_hash
        assert len(tx_hash) == 64
        assert isinstance(tx_hash, str)
        await client.basic.wait_for_tx(hash=tx_hash)

        await asyncio.sleep(3)
        statements = [
            Statement(
                effect=Effect.EFFECT_ALLOW,
                actions=[
                    ActionType.ACTION_UPDATE_BUCKET_INFO,
                    ActionType.ACTION_DELETE_BUCKET,
                ],
            )
        ]
        principal = Principal(type=PrincipalType.PRINCIPAL_TYPE_GNFD_ACCOUNT, value=principal_key_manager.address)
        tx_hash = await client.bucket.put_bucket_policy(
            bucket_name, principal, statements, PutPolicyOption(policy_expire_time=datetime.now() + timedelta(weeks=1))
        )
        assert tx_hash
        assert len(tx_hash) == 64
        assert isinstance(tx_hash, str)
        await client.basic.wait_for_tx(hash=tx_hash)

        head_bucket = await client.bucket.get_bucket_head(bucket_name)
        assert head_bucket

        bucket_policy = await client.bucket.get_bucket_policy(bucket_name, principal_key_manager.address)
        assert bucket_policy
        assert bucket_policy.resource_id == head_bucket.id
        assert isinstance(bucket_policy, Policy)

        principal = Principal(type=PrincipalType.PRINCIPAL_TYPE_GNFD_ACCOUNT, value=principal_key_manager.address)
        tx_hash = await client.bucket.delete_bucket_policy(bucket_name, principal)
        assert tx_hash
        assert len(tx_hash) == 64
        assert isinstance(tx_hash, str)
        await client.basic.wait_for_tx(hash=tx_hash)

        tx_hash = await client.bucket.delete_bucket(bucket_name)
        assert tx_hash
        await client.basic.wait_for_tx(hash=tx_hash)

        # Check that the bucket is deleted
        with pytest.raises(Exception):
            await client.bucket.get_bucket_head(bucket_name)


@pytest.mark.requires_config
@pytest.mark.tx
@pytest.mark.slow
async def test_get_bucket_permission_and_records():
    config = get_account_configuration()
    key_manager = KeyManager(private_key=config.private_key)
    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        await client.async_init()

        bucket_name = "".join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(5, 11)))
        sp = (await client.blockchain_client.get_active_sps())[0]
        tx_hash = await client.bucket.create_bucket(
            bucket_name,
            primary_sp_address=sp["operator_address"],
            opts=CreateBucketOptions(charged_read_quota=100, visibility=VisibilityType.VISIBILITY_TYPE_PRIVATE),
        )
        assert tx_hash
        assert len(tx_hash) == 64
        assert isinstance(tx_hash, str)
        await client.basic.wait_for_tx(hash=tx_hash)

        random_user = KeyManager()
        bucket_permission = await client.bucket.get_bucket_permission(
            random_user.address, bucket_name, ActionType.ACTION_TYPE_ALL
        )
        assert bucket_permission
        assert bucket_permission == Effect(2).name

        bucket_records = await client.bucket.list_bucket_records(bucket_name, ListReadRecordOptions())
        assert bucket_records
        assert len(bucket_records.read_records) == 0
        assert isinstance(bucket_records, ListBucketReadRecord)

        tx_hash = await client.bucket.delete_bucket(bucket_name)
        assert tx_hash
        await client.basic.wait_for_tx(hash=tx_hash)


@pytest.mark.requires_config
@pytest.mark.tx
@pytest.mark.slow
async def test_buy_quota_for_bucket():
    config = get_account_configuration()
    key_manager = KeyManager(private_key=config.private_key)
    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        await client.async_init()

        bucket_name = "".join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(5, 11)))
        sp = (await client.blockchain_client.get_active_sps())[0]
        tx_hash = await client.bucket.create_bucket(
            bucket_name,
            primary_sp_address=sp["operator_address"],
            opts=CreateBucketOptions(charged_read_quota=100, visibility=VisibilityType.VISIBILITY_TYPE_PRIVATE),
        )
        assert tx_hash
        assert len(tx_hash) == 64
        assert isinstance(tx_hash, str)
        await client.basic.wait_for_tx(hash=tx_hash)

        tx_hash = await client.bucket.buy_quota_for_bucket(bucket_name, 1000)
        assert tx_hash
        assert len(tx_hash) == 64
        assert isinstance(tx_hash, str)
        await client.basic.wait_for_tx(hash=tx_hash)

        head_bucket = await client.bucket.get_bucket_head(bucket_name)
        assert head_bucket

        bucket_read_quota = await client.bucket.get_bucket_read_quota(bucket_name)
        assert bucket_read_quota
        assert bucket_read_quota.bucket_name == bucket_name
        assert str(bucket_read_quota.bucket_id) == head_bucket.id
        assert isinstance(bucket_read_quota, ReadQuota)

        tx_hash = await client.bucket.delete_bucket(bucket_name)
        assert tx_hash
        await client.basic.wait_for_tx(hash=tx_hash)


# @pytest.mark.requires_config
# @pytest.mark.tx
# @pytest.mark.slow
# async def test_migrate_bucket():
#     config = get_account_configuration()
#     key_manager = KeyManager(private_key=config.private_key)
#     async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
#         await client.async_init()

#         bucket_name = "".join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(5, 11)))
#         sp = (await client.blockchain_client.get_active_sps())[0]
#         tx_hash = await client.bucket.create_bucket(
#             bucket_name,
#             primary_sp_address=sp["operator_address"],
#             opts=CreateBucketOptions(charged_read_quota=100, visibility=VisibilityType.VISIBILITY_TYPE_PRIVATE),
#         )
#         assert tx_hash
#         assert len(tx_hash) == 64
#         assert isinstance(tx_hash, str)
#         await client.basic.wait_for_tx(hash=tx_hash)

#         sps = await client.storage_provider.list_storage_providers()
#         assert sps
#         assert isinstance(sps, list)

#         tx_hash = await client.bucket.migrate_bucket(bucket_name, sps[1]["id"], MigrateBucketOptions())
#         assert tx_hash
#         assert len(tx_hash) == 64
#         assert isinstance(tx_hash, str)
#         await client.basic.wait_for_tx(hash=tx_hash)

#         await asyncio.sleep(5)

#         meta = await client.bucket.get_bucket_meta(bucket_name, EndPointOptions())
#         assert meta
#         assert isinstance(meta, GetBucketMeta)
#         assert meta.vgf.primary_sp_id == sps[1]["id"]

#         list_buckets = await client.bucket.list_bucket_by_payment_account(
#             key_manager.address, ListBucketsByPaymentAccountOptions()
#         )
#         assert list_buckets
#         assert isinstance(list_buckets, list)
#         assert isinstance(list_buckets[0], ListBucketsByPaymentAccountResponse)

#         tx_hash = await client.bucket.delete_bucket(bucket_name)
#         assert tx_hash
#         await client.basic.wait_for_tx(hash=tx_hash)
