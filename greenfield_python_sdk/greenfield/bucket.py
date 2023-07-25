from typing import List

from betterproto import Casing

from greenfield_python_sdk.blockchain_client import BlockchainClient
from greenfield_python_sdk.key_manager import KeyManager
from greenfield_python_sdk.models.bucket import (
    CreateBucketOptions,
    ListBucketInfo,
    ListBucketReadRecord,
    ListReadRecordOptions,
    ReadQuota,
    UpdateBucketOptions,
)
from greenfield_python_sdk.models.eip712_messages.storage.bucket_url import (
    CREATE_BUCKET,
    DELETE_BUCKET,
    UPDATE_BUCKET_INFO,
)
from greenfield_python_sdk.models.eip712_messages.storage.policy_url import DELETE_POLICY, PUT_POLICY
from greenfield_python_sdk.models.request import Principal, PutPolicyOption, ResourceType
from greenfield_python_sdk.models.transaction import BroadcastOption
from greenfield_python_sdk.protos.greenfield.common import UInt64Value
from greenfield_python_sdk.protos.greenfield.permission import ActionType, Effect, Policy, Statement
from greenfield_python_sdk.protos.greenfield.storage import (
    BucketInfo,
    MsgDeleteBucket,
    MsgDeletePolicy,
    MsgPutPolicy,
    MsgUpdateBucketInfo,
    QueryHeadBucketByIdRequest,
    QueryHeadBucketRequest,
    QueryPolicyForAccountRequest,
    QueryVerifyPermissionRequest,
    VisibilityType,
)
from greenfield_python_sdk.storage_client import StorageClient
from greenfield_python_sdk.storage_provider.utils import check_address, check_valid_bucket_name


class Bucket:
    blockchain_client: BlockchainClient
    key_manager: KeyManager
    storage_client: StorageClient

    def __init__(self, blockchain_client, key_manager, storage_client):
        self.blockchain_client = blockchain_client
        self.key_manager = key_manager
        self.storage_client = storage_client

    async def create_bucket(self, bucket_name: str, primary_sp_address: str, opts: CreateBucketOptions) -> str:
        get_approval, sp_signature = await self.storage_client.bucket.get_bucket_approval(
            bucket_name, primary_sp_address, opts
        )
        tx_hash = await self.blockchain_client.broadcast_message(
            message=get_approval, type_url=CREATE_BUCKET, broadcast_option=BroadcastOption(sp_signature=sp_signature)
        )
        return tx_hash

    async def delete_bucket(self, bucket_name: str) -> str:
        check_valid_bucket_name(bucket_name)

        delete_bucket_msg = MsgDeleteBucket(operator=self.key_manager.address, bucket_name=bucket_name)
        tx_hash = await self.blockchain_client.broadcast_message(message=delete_bucket_msg, type_url=DELETE_BUCKET)
        return tx_hash

    async def update_bucket_visibility(
        self,
        bucket_name: str,
        visibility: VisibilityType,
    ) -> str:
        bucket_info = await self.blockchain_client.storage.get_head_bucket(
            QueryHeadBucketRequest(bucket_name=bucket_name)
        )
        payment_address = check_address(bucket_info.bucket_info.payment_address)

        if visibility == bucket_info.bucket_info.visibility:
            raise Exception(f"The visibility of the bucket is already set to the value {visibility}")

        update_bucket_visibility_msg = MsgUpdateBucketInfo(
            operator=self.key_manager.address,
            bucket_name=bucket_name,
            charged_read_quota=UInt64Value(value=bucket_info.bucket_info.charged_read_quota),
            payment_address=payment_address,
            visibility=visibility,
        )
        tx_hash = await self.blockchain_client.broadcast_message(
            message=update_bucket_visibility_msg, type_url=UPDATE_BUCKET_INFO
        )
        return tx_hash

    async def update_bucket_info(self, bucket_name: str, opts: UpdateBucketOptions) -> str:
        bucket_info = await self.blockchain_client.storage.get_head_bucket(QueryHeadBucketRequest(bucket_name))

        if (
            opts.visibility == bucket_info.bucket_info.visibility
            and opts.charged_read_quota == None
            and opts.payment_address == ""
        ):
            raise Exception("No update option")

        visibility = (
            opts.visibility
            if opts.visibility != bucket_info.bucket_info.visibility
            else bucket_info.bucket_info.visibility
        )
        charged_read_quota = (
            opts.charged_read_quota if opts.charged_read_quota != None else bucket_info.bucket_info.charged_read_quota
        )
        payment_address = (
            check_address(opts.payment_address)
            if opts.payment_address != ""
            else bucket_info.bucket_info.payment_address
        )

        update_bucket_msg = MsgUpdateBucketInfo(
            operator=self.key_manager.address,
            bucket_name=bucket_name,
            charged_read_quota=UInt64Value(value=charged_read_quota),
            payment_address=payment_address,
            visibility=visibility,
        )
        tx_hash = await self.blockchain_client.broadcast_message(message=update_bucket_msg, type_url=UPDATE_BUCKET_INFO)
        return tx_hash

    async def update_bucket_payment_addr(self, bucket_name: str, payment_addr: str) -> str:
        bucket_info = await self.blockchain_client.storage.get_head_bucket(QueryHeadBucketRequest(bucket_name))
        payment_address = check_address(payment_addr)

        update_bucket_payment_address_msg = MsgUpdateBucketInfo(
            operator=self.key_manager.address,
            bucket_name=bucket_name,
            charged_read_quota=UInt64Value(value=bucket_info.bucket_info.charged_read_quota),
            payment_address=payment_address,
            visibility=bucket_info.bucket_info.visibility,
        )
        tx_hash = await self.blockchain_client.broadcast_message(
            message=update_bucket_payment_address_msg, type_url=UPDATE_BUCKET_INFO
        )
        return tx_hash

    async def get_bucket_head(self, bucket_name: str) -> BucketInfo:
        try:
            bucket_info = await self.blockchain_client.storage.get_head_bucket(QueryHeadBucketRequest(bucket_name))
        except Exception:
            raise Exception("Bucket not found")

        if bucket_info.bucket_info == None:
            raise Exception("Bucket not found")
        return bucket_info.bucket_info

    async def get_head_bucket_by_id(self, bucket_id: str) -> BucketInfo:
        bucket_info = await self.blockchain_client.storage.get_head_bucket_by_id(QueryHeadBucketByIdRequest(bucket_id))

        if bucket_info.bucket_info == None:
            raise Exception("Bucket not found")
        return bucket_info.bucket_info

    async def put_bucket_policy(
        self,
        bucket_name: str,
        principal: Principal,
        statements: List[Statement],
        opts: PutPolicyOption,
    ) -> str:
        resource = f"grn:{ResourceType.RESOURCE_TYPE_BUCKET.value}::{bucket_name}"
        put_policy_msg = MsgPutPolicy(
            operator=self.key_manager.address,
            resource=str(resource),
            principal=principal,
            statements=statements,
        )
        if opts.policy_expire_time:
            put_policy_msg.expiration_time = opts.policy_expire_time

        tx_hash = await self.blockchain_client.broadcast_message(message=put_policy_msg, type_url=PUT_POLICY)
        return tx_hash

    async def delete_bucket_policy(self, bucket_name: str, principal: Principal) -> str:
        resource = f"grn:{ResourceType.RESOURCE_TYPE_BUCKET.value}::{bucket_name}"

        delete_policy_msg = MsgDeletePolicy(
            operator=self.key_manager.address,
            resource=str(resource),
            principal=principal,
        )
        tx_hash = await self.blockchain_client.broadcast_message(message=delete_policy_msg, type_url=DELETE_POLICY)
        return tx_hash

    async def get_bucket_policy(self, bucket_name: str, principal_addr: str) -> Policy:
        resource = f"grn:{ResourceType.RESOURCE_TYPE_BUCKET.value}::{bucket_name}"
        policy = await self.blockchain_client.storage.get_policy_for_account(
            QueryPolicyForAccountRequest(resource, principal_addr)
        )

        if policy.policy == None:
            raise Exception("Policy not found")
        return policy.policy

    async def get_bucket_permission(self, user_addr: str, bucket_name: str, action: ActionType) -> Effect:
        check_valid_bucket_name(bucket_name)
        effect = await self.blockchain_client.storage.verify_permission(
            QueryVerifyPermissionRequest(operator=user_addr, bucket_name=bucket_name, action_type=action)
        )

        if effect.effect == None:
            raise Exception("Effect not found")
        return Effect(effect.effect).name

    async def list_buckets(self, sp_address: str) -> List[ListBucketInfo]:
        return await self.storage_client.bucket.list_buckets(sp_address)

    async def list_bucket_records(self, bucket_name: str, opts: ListReadRecordOptions) -> ListBucketReadRecord:
        response = await self.blockchain_client.storage.get_head_bucket(QueryHeadBucketRequest(bucket_name=bucket_name))
        primary_sp_address = response.to_pydict(casing=Casing.SNAKE)["bucket_info"]["primary_sp_address"]
        return await self.storage_client.bucket.list_bucket_read_record(bucket_name, primary_sp_address, opts)

    async def buy_quota_for_bucket(self, bucket_name: str, target_quota: int) -> str:
        bucket_info = await self.blockchain_client.storage.get_head_bucket(
            QueryHeadBucketRequest(bucket_name=bucket_name)
        )
        payment_address = check_address(bucket_info.bucket_info.payment_address)

        update_quota_bucket_msg = MsgUpdateBucketInfo(
            operator=self.key_manager.address,
            bucket_name=bucket_name,
            charged_read_quota=UInt64Value(value=target_quota),
            payment_address=payment_address,
            visibility=bucket_info.bucket_info.visibility,
        )
        tx_hash = await self.blockchain_client.broadcast_message(
            message=update_quota_bucket_msg, type_url=UPDATE_BUCKET_INFO
        )
        return tx_hash

    async def get_bucket_read_quota(self, bucket_name: str) -> ReadQuota:
        response = await self.blockchain_client.storage.get_head_bucket(QueryHeadBucketRequest(bucket_name=bucket_name))
        primary_sp_address = response.to_pydict(casing=Casing.SNAKE)["bucket_info"]["primary_sp_address"]
        return await self.storage_client.bucket.get_bucket_read_quota(bucket_name, primary_sp_address)
