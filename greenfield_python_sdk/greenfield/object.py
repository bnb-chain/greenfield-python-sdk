import io
import os
from typing import Any, List, Tuple

from betterproto import Casing

from greenfield_python_sdk.blockchain_client import BlockchainClient
from greenfield_python_sdk.key_manager import KeyManager
from greenfield_python_sdk.models.bucket import VisibilityType
from greenfield_python_sdk.models.eip712_messages.storage.object_url import (
    CANCEL_CREATE_OBJECT,
    CREATE_OBJECT,
    DELETE_OBJECT,
    UPDATE_OBJECT_INFO,
)
from greenfield_python_sdk.models.eip712_messages.storage.policy_url import DELETE_POLICY, PUT_POLICY
from greenfield_python_sdk.models.object import (
    CreateObjectOptions,
    GetObjectOption,
    ListObjectsOptions,
    ListObjectsResult,
    PutObjectOptions,
)
from greenfield_python_sdk.models.request import Principal, PutPolicyOption, ResourceType
from greenfield_python_sdk.models.transaction import BroadcastOption
from greenfield_python_sdk.protos.greenfield.permission import ActionType, Effect, Policy, Statement
from greenfield_python_sdk.protos.greenfield.storage import (
    MsgCancelCreateObject,
    MsgDeleteObject,
    MsgDeletePolicy,
    MsgPutPolicy,
    MsgUpdateObjectInfo,
    ObjectInfo,
    QueryHeadBucketRequest,
    QueryHeadObjectByIdRequest,
    QueryHeadObjectRequest,
    QueryPolicyForAccountRequest,
    QueryVerifyPermissionRequest,
)
from greenfield_python_sdk.storage_client import StorageClient
from greenfield_python_sdk.storage_provider.utils import check_valid_bucket_name, check_valid_object_name


class Object:
    blockchain_client: BlockchainClient
    key_manager: KeyManager
    storage_client: StorageClient

    def __init__(self, blockchain_client, key_manager, storage_client):
        self.blockchain_client = blockchain_client
        self.key_manager = key_manager
        self.storage_client = storage_client

    async def create_object(
        self, bucket_name: str, object_name: str, reader: io.BytesIO, opts: CreateObjectOptions
    ) -> str:
        sp = await self.blockchain_client.sp.get_first_in_service_storage_provider()

        storage_params = await self.blockchain_client.storage.get_params()
        get_approval, sp_signature, checksums = await self.storage_client.object.get_object_approval(
            bucket_name, object_name, opts, sp["operator_address"], reader, storage_params
        )
        response = await self.blockchain_client.broadcast_message(
            message=get_approval,
            type_url=CREATE_OBJECT,
            broadcast_option=BroadcastOption(sp_signature=sp_signature, checksums=checksums),
        )
        return response

    async def put_object(
        self,
        bucket_name: str,
        object_name: str,
        object_size: int,
        reader: io.BytesIO,
        opts: PutObjectOptions,
    ) -> str:
        sp = await self.blockchain_client.sp.get_first_in_service_storage_provider()
        return await self.storage_client.object.put_object(
            bucket_name, object_name, object_size, sp["operator_address"], reader, opts
        )

    async def cancel_create_object(self, bucket_name: str, object_name: str) -> str:
        check_valid_bucket_name(bucket_name)
        check_valid_object_name(object_name)
        cancel_create_object = MsgCancelCreateObject(
            operator=self.key_manager.address,
            bucket_name=bucket_name,
            object_name=object_name,
        )
        response = await self.blockchain_client.broadcast_message(
            message=cancel_create_object, type_url=CANCEL_CREATE_OBJECT
        )
        return response

    async def delete_object(self, bucket_name: str, object_name: str) -> str:
        check_valid_bucket_name(bucket_name)
        check_valid_object_name(object_name)

        delete_object_msg = MsgDeleteObject(
            operator=self.key_manager.address, bucket_name=bucket_name, object_name=object_name
        )
        response = await self.blockchain_client.broadcast_message(message=delete_object_msg, type_url=DELETE_OBJECT)
        return response

    async def get_object(self, bucket_name: str, object_name: str, opts: GetObjectOption) -> Tuple[Any, ObjectInfo]:
        sp = await self.blockchain_client.sp.get_first_in_service_storage_provider()

        return await self.storage_client.object.get_object(bucket_name, object_name, opts, sp["operator_address"])

    async def get_object_head(self, bucket_name: str, object_name: str) -> ObjectInfo:
        object_info = await self.blockchain_client.storage.get_head_object(
            QueryHeadObjectRequest(bucket_name, object_name)
        )

        if object_info.object_info == None:
            raise Exception("Object not found")
        return object_info.object_info

    async def get_object_head_by_id(self, object_id: str) -> ObjectInfo:
        object_info = await self.blockchain_client.storage.get_head_object_by_id(QueryHeadObjectByIdRequest(object_id))

        if object_info.object_info == None:
            raise Exception("Object not found")
        return object_info.object_info

    async def update_object_visibility(self, bucket_name: str, object_name: str, visibility: VisibilityType) -> str:
        object_info = await self.blockchain_client.storage.get_head_object(
            QueryHeadObjectRequest(bucket_name, object_name)
        )

        if object_info.object_info == None:
            raise Exception("Object not found")

        if visibility == object_info.object_info.visibility:
            raise Exception(f"The visibility of the object is already set to the value {visibility}")

        update_object_visibility_msg = MsgUpdateObjectInfo(
            operator=self.key_manager.address,
            bucket_name=bucket_name,
            object_name=object_name,
            visibility=visibility,
        )
        response = await self.blockchain_client.broadcast_message(
            message=update_object_visibility_msg, type_url=UPDATE_OBJECT_INFO
        )
        return response

    async def put_object_policy(
        self,
        bucket_name: str,
        object_name: str,
        principal: Principal,
        statements: List["Statement"],
        opts: PutPolicyOption = None,
    ) -> str:
        resource = f"grn:{ResourceType.RESOURCE_TYPE_OBJECT.value}::{bucket_name}/{object_name}"

        put_policy_msg = MsgPutPolicy(
            operator=self.key_manager.address,
            resource=str(resource),
            principal=principal,
            statements=statements,
        )
        if opts and opts.policy_expire_time:
            put_policy_msg.expiration_time = opts.policy_expire_time
        response = await self.blockchain_client.broadcast_message(message=put_policy_msg, type_url=PUT_POLICY)
        return response

    async def delete_object_policy(self, bucket_name: str, object_name: str, principal: Principal) -> str:
        resource = f"grn:{ResourceType.RESOURCE_TYPE_OBJECT.value}::{bucket_name}/{object_name}"

        delete_policy_msg = MsgDeletePolicy(
            operator=self.key_manager.address,
            resource=str(resource),
            principal=principal,
        )
        response = await self.blockchain_client.broadcast_message(message=delete_policy_msg, type_url=DELETE_POLICY)
        return response

    async def get_object_policy(self, bucket_name: str, object_name: str, principal_addr: str) -> Policy:
        resource = f"grn:{ResourceType.RESOURCE_TYPE_OBJECT.value}::{bucket_name}/{object_name}"
        policy = await self.blockchain_client.storage.get_policy_for_account(
            QueryPolicyForAccountRequest(resource, principal_addr)
        )

        if policy.policy == None:
            raise Exception("Policy not found")
        return policy.policy

    async def get_object_permission(
        self, user_addr: str, bucket_name: str, object_name: str, action: ActionType
    ) -> Effect:
        check_valid_bucket_name(bucket_name)
        check_valid_object_name(object_name)
        effect = await self.blockchain_client.storage.verify_permission(
            QueryVerifyPermissionRequest(user_addr, bucket_name, object_name, action)
        )

        if effect.effect == None:
            raise Exception("Effect not found")
        return Effect(effect.effect).name

    async def list_objects(self, bucket_name: str, opts: ListObjectsOptions) -> ListObjectsResult:
        sp = await self.blockchain_client.sp.get_first_in_service_storage_provider()
        return await self.storage_client.object.list_objects(bucket_name, opts, sp["operator_address"])

    async def create_folder(self, bucket_name: str, object_name: str, opts: CreateObjectOptions) -> str:
        if object_name.endswith("/") == False:
            raise Exception("Folder names must end with a forward slash (/) character")
        return await self.create_object(bucket_name, object_name, io.BytesIO(), opts)

    async def fput_object(self, bucket_name: str, object_name: str, file_path: str, opts: PutObjectOptions) -> str:
        with open(file_path, "r") as file:
            lines = file.read()
        try:
            data = io.BytesIO(lines.encode("utf-8"))
        except Exception:
            data = io.BytesIO(lines)

        res = await self.put_object(bucket_name, object_name, data.getbuffer().nbytes, data, opts)
        return res

    async def fget_object(self, bucket_name: str, object_name: str, file_path: str, opts: GetObjectOption):
        if os.path.isdir(file_path):
            raise Exception("File name is a folder")

        if os.path.exists(file_path):
            file = open(file_path, "a")
        else:
            file = open(file_path, "w+")

        _, data = await self.get_object(bucket_name, object_name, opts)
        file.write(data)
        file.close()
