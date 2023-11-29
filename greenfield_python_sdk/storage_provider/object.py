import base64
import binascii
import io
import json
import re
from datetime import datetime, timedelta
from typing import Any, List, Tuple

import html_to_json

from greenfield_python_sdk.models.bucket import EndPointOptions
from greenfield_python_sdk.models.const import CREATE_OBJECT_ACTION
from greenfield_python_sdk.models.object import (
    CreateObjectOptions,
    GetObjectOption,
    ListObjectPoliciesOptions,
    ListObjectsOptions,
    ListObjectsResult,
    ObjectMeta,
    ObjectPolicies,
    PutObjectOptions,
)
from greenfield_python_sdk.models.request import AminAPIInfo, RequestMeta, SendOptions
from greenfield_python_sdk.protos.greenfield.common import Approval
from greenfield_python_sdk.protos.greenfield.permission import ActionType
from greenfield_python_sdk.protos.greenfield.storage import MsgCreateObject, ObjectInfo, RedundancyType, VisibilityType
from greenfield_python_sdk.storage_provider.request import Client
from greenfield_python_sdk.storage_provider.utils import (
    check_valid_bucket_name,
    check_valid_object_name,
    compute_integrity_hash_go,
    convert_key,
    convert_value,
    get_obj_info,
    get_unsigned_bytes_from_message,
    is_valid_object_prefix,
)


class Object:
    def __init__(self, client: Client):
        self.client = client

    async def get_object_approval(
        self,
        bucket_name: str,
        object_name: str,
        opts: CreateObjectOptions,
        primary_sp_address: str,
        reader: io.BytesIO,
        storage_params,
        is_serial_compute_mode: str,
    ) -> Tuple[MsgCreateObject, str, List[str]]:
        check_valid_bucket_name(bucket_name)
        check_valid_object_name(object_name)

        expect_check_Sums, size, redundancy_type = await self.compute_hash_roots(
            storage_params, reader, is_serial_compute_mode
        )

        if opts.content_type != "" and opts.content_type != None:
            content_type = opts.content_type
        else:
            content_type = "application/octet-stream"

        if opts.visibility == VisibilityType.VISIBILITY_TYPE_UNSPECIFIED or opts.visibility == None:
            visibility = VisibilityType.VISIBILITY_TYPE_INHERIT
        else:
            visibility = opts.visibility

        create_object_msg = MsgCreateObject(
            bucket_name=bucket_name,
            content_type=content_type,
            creator=self.client.key_manager.address,
            expect_checksums=expect_check_Sums,
            object_name=object_name,
            payload_size=size,
            primary_sp_approval=Approval(expired_height=0),
            redundancy_type=redundancy_type,
            visibility=visibility,
        )

        approval_signed_message = await self.create_object_approval(create_object_msg, primary_sp_address)
        json_signed_message = json.loads(approval_signed_message.decode("utf-8"))
        checksums = json_signed_message["expect_checksums"]
        expired_height = int(json_signed_message["primary_sp_approval"]["expired_height"])
        create_object_msg.primary_sp_approval = Approval(
            expired_height=expired_height,
            sig=bytes(json_signed_message["primary_sp_approval"]["sig"], "utf-8"),
        )
        return (
            create_object_msg,
            json_signed_message["primary_sp_approval"]["sig"],
            checksums,
        )

    async def compute_hash_roots(
        self, storage_params, reader: io.BytesIO, is_serial_compute_mode: str
    ) -> Tuple[List[bytes], int, RedundancyType]:
        data_blocks = storage_params.params.versioned_params.redundant_data_chunk_num
        parity_blocks = storage_params.params.versioned_params.redundant_parity_chunk_num
        seg_size = storage_params.params.versioned_params.max_segment_size

        expectCheckSums, size, redundancy_type = compute_integrity_hash_go(
            reader, int(seg_size), int(data_blocks), int(parity_blocks), is_serial_compute_mode
        )
        return expectCheckSums, size, redundancy_type

    async def put_object(
        self,
        bucket_name: str,
        object_name: str,
        object_size: int,
        primary_sp_address: str,
        reader: bytes,
        opts: PutObjectOptions,
    ) -> str:
        if object_size < 0:
            raise ValueError("object_size must be greater than 0")

        check_valid_bucket_name(bucket_name)
        check_valid_object_name(object_name)

        if opts.content_type != "" and opts.content_type != None:
            content_type = opts.content_type
        else:
            content_type = "application/octet-stream"

        if opts.txn_hash != "" and opts.txn_hash != None:
            send_opt = SendOptions(method="PUT", body=reader, txn_hash=opts.txn_hash)
        else:
            send_opt = SendOptions(method="PUT", body=reader)

        base_url = await self.client._get_sp_url_by_addr(primary_sp_address, bucket_name)
        expiry = (datetime.utcnow() + timedelta(seconds=1000)).strftime("%Y-%m-%dT%H:%M:%SZ")
        request_metadata = RequestMeta(
            method="PUT",
            bucket_name=bucket_name,
            object_name=object_name,
            content_type=content_type,
            content_length=object_size,
            base_url=base_url,
            expiry_timestamp=expiry,
        ).model_dump()

        response = await self.client.prepare_request(
            base_url,
            request_metadata,
            body=send_opt.body,
        )
        if response.status != 200:
            raise ValueError("put object failed")
        return "Object added successfully"

    async def get_object(
        self,
        bucket_name: str,
        object_name: str,
        primary_sp_address: str,
        opts: GetObjectOption,
    ) -> Tuple[Any, ObjectInfo]:
        check_valid_bucket_name(bucket_name)
        check_valid_object_name(object_name)

        base_url = await self.client._get_sp_url_by_addr(primary_sp_address, bucket_name)
        expiry = (datetime.utcnow() + timedelta(seconds=1000)).strftime("%Y-%m-%dT%H:%M:%SZ")
        request_metadata = RequestMeta(
            bucket_name=bucket_name,
            object_name=object_name,
            base_url=base_url,
            disable_close_body=True,
            expiry_timestamp=expiry,
        ).model_dump()

        if opts.range != "":
            request_metadata["range_info"] = opts.range

        response = await self.client.prepare_request(
            base_url,
            request_metadata,
        )
        info = get_obj_info(object_name, response)
        res = await response.text()
        return info, res

    async def list_objects(
        self, bucket_name: str, primary_sp_address: str, opts: ListObjectsOptions
    ) -> ListObjectsResult:
        check_valid_bucket_name(bucket_name)

        if opts.max_keys == 0 or opts.max_keys == None:
            opts.max_keys = 50

        if opts.max_keys > 1000:
            raise ValueError("max-keys must be less than or equal to 1000")

        if opts.start_after != "":
            check_valid_object_name(opts.start_after)

        if opts.continuation_token != "":
            decoded_continuation_token = base64.b64decode(opts.continuation_token)
            opts.continuation_token = str(decoded_continuation_token, "utf-8")
            check_valid_object_name(opts.continuation_token)
            if opts.continuation_token.startswith(opts.prefix) == False:
                raise ValueError("continuation-token does not match the input prefix")

        if opts.prefix != "":
            is_valid_object_prefix(opts.prefix)

        query_parameters = {
            "continuation-token": opts.continuation_token,
            "delimiter": opts.delimiter,
            "max-keys": opts.max_keys,
            "prefix": opts.prefix,
            "start-after": opts.start_after,
        }

        base_url = await self.client._get_sp_url_by_addr(primary_sp_address, bucket_name)
        request_metadata = RequestMeta(
            base_url=base_url,
            disable_close_body=True,
        ).model_dump()

        response = await self.client.prepare_request(base_url, request_metadata, query_parameters)
        res = html_to_json.convert(await response.text())["gfsplistobjectsbybucketnameresponse"][0]
        if "objects" in res:
            current_object = []
            for _, object_info in enumerate(res["objects"]):
                converted_data_list = {
                    convert_key(key): convert_value(key, value) if value[0] else ""
                    for key, value in object_info.items()
                }
                if converted_data_list["removed"] == False:
                    current_object.append(
                        {
                            "object_name": converted_data_list["object_info"]["object_name"],
                            "id": converted_data_list["object_info"]["id"],
                            "payload_size": converted_data_list["object_info"]["payload_size"],
                            "visibility": converted_data_list["object_info"]["visibility"].name,
                            "content_type": converted_data_list["object_info"]["content_type"],
                            "checksums": converted_data_list["object_info"]["checksums"],
                            "create_at": converted_data_list["object_info"]["create_at"],
                        }
                    )
            res.pop("objects")
            res = {convert_key(key): convert_value(key, value) for key, value in res.items()}
            res["objects"] = current_object
        else:
            res = {convert_key(key): convert_value(key, value) for key, value in res.items()}
            res["objects"] = []
        return ListObjectsResult(**res)

    async def create_object_approval(self, create_object_msg: MsgCreateObject, primary_sp_address: str) -> str:
        unsigned_bytes = get_unsigned_bytes_from_message(create_object_msg)
        query_parameters = {"action": CREATE_OBJECT_ACTION}
        endpoint = "get-approval"
        base_url = await self.client._get_sp_url_by_addr(primary_sp_address)

        expiry = (datetime.utcnow() + timedelta(seconds=1000)).strftime("%Y-%m-%dT%H:%M:%SZ")
        request_metadata = RequestMeta(
            query_parameters=query_parameters,
            txn_msg=binascii.hexlify(unsigned_bytes),
            base_url=base_url,
            endpoint=endpoint,
            expiry_timestamp=expiry,
            admin_api_info=AminAPIInfo(is_admin_api=True, admin_version=1),
        ).model_dump()

        response = await self.client.prepare_request(
            base_url,
            request_metadata,
            request_metadata["query_parameters"],
            request_metadata["endpoint"],
        )
        signed_raw_msg = response.headers.get("X-Gnfd-Signed-Msg")
        return binascii.unhexlify(signed_raw_msg)

    async def list_object_by_object_id(self, object_ids: List[int], opts: EndPointOptions) -> List[ObjectMeta]:
        maximum_list_objects_size = 100
        if len(object_ids) == 0 and len(object_ids) > maximum_list_objects_size:
            raise ValueError("object_ids must be less than or equal to 100")

        query_parameters = {"objects-query": "", "ids": ",".join([str(i) for i in object_ids])}
        base_url = await self.client.get_url(opts.endpoint, opts.sp_address)

        request_metadata = RequestMeta(disable_close_body=True, query_parameters=query_parameters).model_dump()

        response = await self.client.prepare_request(
            base_url,
            request_metadata,
            request_metadata["query_parameters"],
        )
        list_object = html_to_json.convert(await response.text())["gfsplistobjectsbyidsresponse"][0]["objectentry"]
        current_object = []

        if "value" in list_object[0]:
            for _, object in enumerate(list_object):
                converted_data_list = {
                    convert_key(key): convert_value(key, value) if value[0] else "" for key, value in object.items()
                }
                current_object.append(ObjectMeta(**converted_data_list["value"]))

        return current_object

    async def list_object_policies(
        self,
        bucket_name: str,
        object_name: str,
        sp_address: str,
        action_type: ActionType,
        opts: ListObjectPoliciesOptions,
    ) -> List[ObjectPolicies]:
        query_parameters = {
            "object-policies": "",
            "start-after": opts.start_after,
            "limit": int(opts.limit),
            "action-type": action_type,
        }
        base_url = await self.client._get_sp_url_by_addr(sp_address, bucket_name)

        request_metadata = RequestMeta(
            disable_close_body=True, query_parameters=query_parameters, bucket_name=bucket_name, object_name=object_name
        ).model_dump()
        response = await self.client.prepare_request(
            base_url,
            request_metadata,
            request_metadata["query_parameters"],
        )
        list_policies = html_to_json.convert(await response.text())["gfsplistobjectpoliciesresponse"][0]
        policies = []
        if "policies" in list_policies:
            for _, object in enumerate(list_policies["policies"]):
                converted_data_list = {
                    convert_key(key): convert_value(key, value) if value[0] else "" for key, value in object.items()
                }
                policies.append(ObjectPolicies(**converted_data_list))
        return policies
