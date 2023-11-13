import binascii
import json
import re
from datetime import datetime, timedelta
from typing import List, Tuple

import html_to_json
import xmltodict

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
)
from greenfield_python_sdk.models.const import CREATE_BUCKET_ACTION, MIGRATE_BUCKET_ACTION
from greenfield_python_sdk.models.request import RequestMeta
from greenfield_python_sdk.protos.greenfield.common import Approval
from greenfield_python_sdk.protos.greenfield.storage import MsgCreateBucket, MsgMigrateBucket
from greenfield_python_sdk.storage_provider.request import Client
from greenfield_python_sdk.storage_provider.utils import (
    check_valid_bucket_name,
    convert_key,
    convert_value,
    get_unsigned_bytes_from_message,
)


class Bucket:
    def __init__(self, client: Client):
        self.client = client

    async def get_bucket_approval(
        self,
        bucket_name: str,
        primary_sp_address: str,
        opts: CreateBucketOptions,
    ) -> Tuple[MsgCreateBucket, str]:
        create_bucket_msg = MsgCreateBucket(
            creator=opts.creator_address or self.client.key_manager.address,
            bucket_name=bucket_name,
            visibility=opts.visibility,
            payment_address=opts.payment_address or self.client.key_manager.address,
            primary_sp_address=primary_sp_address,
            primary_sp_approval=opts.primary_sp_approval,
            charged_read_quota=opts.charged_read_quota,
        )
        approval_signed_message = await self.get_create_bucket_approval(create_bucket_msg)
        json_signed_message = json.loads(approval_signed_message.decode("utf-8"))

        expired_height = int(json_signed_message["primary_sp_approval"]["expired_height"])
        create_bucket_msg.primary_sp_approval = Approval(
            expired_height=expired_height,
            global_virtual_group_family_id=int(
                json_signed_message["primary_sp_approval"]["global_virtual_group_family_id"]
            ),
            sig=bytes(json_signed_message["primary_sp_approval"]["sig"], "utf-8"),
        )
        return create_bucket_msg, json_signed_message["primary_sp_approval"]["sig"]

    async def list_buckets(self, sp_address: str) -> List[ListBucketInfo]:
        base_url = await self.client._get_sp_url_by_addr(sp_address)
        request_metadata = RequestMeta(
            base_url=base_url,
            user_address=self.client.key_manager.address,
        ).model_dump()
        response = await self.client.prepare_request(base_url, request_metadata)
        list_bucket_info = html_to_json.convert(await response.text())

        buckets = []
        if "gfspgetuserbucketsresponse" in list_bucket_info:
            list_bucket_info = list_bucket_info["gfspgetuserbucketsresponse"][0]["buckets"]
            for _, bucket_info in enumerate(list_bucket_info):
                converted_data = {
                    convert_key(key): convert_value(key, value) if value[0] else ""
                    for key, value in bucket_info.items()
                }
                buckets.append(ListBucketInfo(**converted_data))

        return buckets

    async def list_bucket_read_record(
        self, bucket_name: str, primary_sp_address, opts: ListReadRecordOptions
    ) -> ListBucketReadRecord:
        check_valid_bucket_name(bucket_name)

        if opts.start_time_stamp < 0:
            raise Exception("Timestamp must be greater than 0")

        time_now = datetime.now()
        time_today = datetime(time_now.year, time_now.month, time_now.day, 0, 0, 0, 0, time_now.tzinfo)
        start_time_stamp = (
            int((time_today + timedelta(days=1 - time_today.day)).timestamp()) * 1000000
            if opts.start_time_stamp == 0
            else opts.start_time_stamp
        )
        time_month_end = int((time_today + timedelta(days=32 - time_today.day)).replace(day=1).timestamp() * 1000000)

        if start_time_stamp > time_month_end:
            raise Exception("Timestamp must be less than the end of the month")

        query_parameters = {
            "end-timestamp": str(time_month_end),
            "list-read-record": "",
        }

        query_parameters["max-records"] = opts.max_records if opts.max_records > 0 else 1000
        query_parameters["start-timestamp"] = str(start_time_stamp)

        base_url = await self.client._get_sp_url_by_addr(primary_sp_address, bucket_name)
        expiry = (datetime.utcnow() + timedelta(seconds=1000)).strftime("%Y-%m-%dT%H:%M:%SZ")
        request_metadata = RequestMeta(
            query_parameters=query_parameters,
            disable_close_body=True,
            base_url=base_url,
            expiry_timestamp=expiry,
        ).model_dump()

        response = await self.client.prepare_request(base_url, request_metadata, request_metadata["query_parameters"])
        result = xmltodict.parse(await response.text())["GetBucketReadQuotaResult"]

        return (
            ListBucketReadRecord(
                next_start_timestamp_us=int(result["NextStartTimestampUs"]),
                read_records=result["read_records"],
            )
            if "read_records" in result
            else ListBucketReadRecord(
                next_start_timestamp_us=int(result["NextStartTimestampUs"]),
            )
        )

    async def get_bucket_read_quota(self, bucket_name: str, primary_sp_address) -> ReadQuota:
        year, month, _ = (
            datetime.now().date().year,
            datetime.now().date().month,
            datetime.now().date().day,
        )
        date = f"{year}-0{month}" if month < 10 else f"{year}-{month}"
        query_parameters = {"read-quota": "", "year-month": date}

        base_url = await self.client._get_sp_url_by_addr(primary_sp_address, bucket_name)
        expiry = (datetime.utcnow() + timedelta(seconds=1000)).strftime("%Y-%m-%dT%H:%M:%SZ")
        request_metadata = RequestMeta(
            query_parameters=query_parameters,
            disable_close_body=True,
            base_url=base_url,
            expiry_timestamp=expiry,
        ).model_dump()

        response = await self.client.prepare_request(base_url, request_metadata, request_metadata["query_parameters"])

        result = xmltodict.parse(await response.text())["GetReadQuotaResult"]

        return ReadQuota(
            bucket_name=bucket_name,
            bucket_id=int(result["BucketID"]),
            read_quota_size=int(result["ReadQuotaSize"]),
            sp_free_read_quota_size=int(result["SPFreeReadQuotaSize"]),
            read_consumed_size=int(result["ReadConsumedSize"]),
        )

    async def get_create_bucket_approval(self, create_bucket_msg: MsgCreateBucket) -> str:
        unsigned_bytes = get_unsigned_bytes_from_message(create_bucket_msg)
        base_url = await self.client._get_sp_url_by_addr(create_bucket_msg.primary_sp_address)

        query_parameters = {"action": CREATE_BUCKET_ACTION}
        endpoint = "get-approval"

        expiry = (datetime.utcnow() + timedelta(seconds=1000)).strftime("%Y-%m-%dT%H:%M:%SZ")
        request_metadata = RequestMeta(
            query_parameters=query_parameters,
            txn_msg=binascii.hexlify(unsigned_bytes),
            is_admin_api=True,
            base_url=base_url,
            endpoint=endpoint,
            expiry_timestamp=expiry,
        ).model_dump()

        response = await self.client.prepare_request(
            base_url,
            request_metadata,
            request_metadata["query_parameters"],
            request_metadata["endpoint"],
            request_metadata["is_admin_api"],
        )
        signed_raw_msg = response.headers.get("X-Gnfd-Signed-Msg")
        signed_msg_bytes = binascii.unhexlify(signed_raw_msg)
        return signed_msg_bytes

    async def list_buckets_by_bucket_id(
        self, bucket_id: List[int], opts: EndPointOptions
    ) -> List[ListBucketsByBucketIDResponse]:
        maximum_list_buckets_size = 1000
        if len(bucket_id) > maximum_list_buckets_size or len(bucket_id) == 0:
            return ListBucketsByBucketIDResponse()

        query_parameters = {"buckets-query": "", "ids": ",".join([str(i) for i in bucket_id])}

        base_url = await self.client.get_url(opts.endpoint, opts.sp_address)

        request_metadata = RequestMeta(
            disable_close_body=True, query_parameters=query_parameters, content_type="application/json"
        ).model_dump()
        response = await self.client.prepare_request(
            base_url,
            request_metadata,
            request_metadata["query_parameters"],
        )
        list_bucket = html_to_json.convert(await response.text())["gfsplistbucketsbyidsresponse"][0]["bucketentry"]
        current_bucket = []
        if "value" in list_bucket[0]:
            for _, bucket in enumerate(list_bucket):
                converted_data_list = {
                    convert_key(key): convert_value(key, value) if value[0] else "" for key, value in bucket.items()
                }
                current_bucket.append(ListBucketsByBucketIDResponse(**converted_data_list["value"]))

        return current_bucket

    async def get_migrate_bucket_approval(
        self, bucket_name: str, dst_primary_sp_id: int, opts: MigrateBucketOptions
    ) -> Tuple[MsgMigrateBucket, str]:
        migrate_bucket_msg = MsgMigrateBucket(
            operator=self.client.key_manager.address,
            bucket_name=bucket_name,
            dst_primary_sp_id=dst_primary_sp_id,
            dst_primary_sp_approval=Approval(expired_height=0),
        )
        unsigned_bytes = get_unsigned_bytes_from_message(migrate_bucket_msg)

        query_parameters = {"action": MIGRATE_BUCKET_ACTION}
        endpoint = "get-approval"

        base_url = await self.client._get_sp_url_by_id(dst_primary_sp_id)
        expiry = (datetime.utcnow() + timedelta(seconds=1000)).strftime("%Y-%m-%dT%H:%M:%SZ")
        request_metadata = RequestMeta(
            query_parameters=query_parameters,
            txn_msg=binascii.hexlify(unsigned_bytes),
            is_admin_api=True,
            base_url=base_url,
            endpoint=endpoint,
            content_type="application/octet-stream",
            expiry_timestamp=expiry,
        ).model_dump()

        response = await self.client.prepare_request(
            base_url,
            request_metadata,
            request_metadata["query_parameters"],
            request_metadata["endpoint"],
            request_metadata["is_admin_api"],
        )
        signed_raw_msg = response.headers.get("X-Gnfd-Signed-Msg")
        signed_msg_bytes = binascii.unhexlify(signed_raw_msg)

        json_signed_message = json.loads(signed_msg_bytes.decode("utf-8"))

        expired_height = int(json_signed_message["dst_primary_sp_approval"]["expired_height"])
        migrate_bucket_msg.dst_primary_sp_approval = Approval(
            expired_height=expired_height,
            global_virtual_group_family_id=int(
                json_signed_message["dst_primary_sp_approval"]["global_virtual_group_family_id"]
            ),
            sig=bytes(json_signed_message["dst_primary_sp_approval"]["sig"], "utf-8"),
        )
        return migrate_bucket_msg, json_signed_message["dst_primary_sp_approval"]["sig"]

    async def list_bucket_by_payment_account(
        self, payment_account: str, opts: ListBucketsByPaymentAccountOptions
    ) -> List[ListBucketsByPaymentAccountResponse]:
        query_parameters = {"payment-buckets": "", "payment-account": payment_account}
        request_metadata = RequestMeta(disable_close_body=True, query_parameters=query_parameters).model_dump()

        base_url = await self.client.get_url(opts.endpoint, opts.sp_address)

        response = await self.client.prepare_request(
            base_url,
            request_metadata,
            request_metadata["query_parameters"],
        )
        list_bucket = html_to_json.convert(await response.text())["gfsplistpaymentaccountstreamsresponse"][0]["buckets"]
        current_bucket = []

        if "bucketinfo" in list_bucket[0]:
            for _, bucket in enumerate(list_bucket):
                converted_data_list = {
                    convert_key(key): convert_value(key, value) if value[0] else "" for key, value in bucket.items()
                }
                current_bucket.append(ListBucketsByPaymentAccountResponse(**converted_data_list))

        return current_bucket

    async def get_bucket_meta(self, bucket_name: str, opts: EndPointOptions) -> GetBucketMeta:
        query_parameters = {"bucket-meta": ""}
        request_metadata = RequestMeta(
            disable_close_body=True, query_parameters=query_parameters, bucket_name=bucket_name
        ).model_dump()

        base_url = await self.client.get_url(opts.endpoint, opts.sp_address)
        response = await self.client.prepare_request(
            base_url,
            request_metadata,
            request_metadata["query_parameters"],
        )
        meta = html_to_json.convert(await response.text())["gfspgetbucketmetaresponse"]

        if "bucket" in meta[0]:
            for _, bucket in enumerate(meta):
                converted_data_list = {
                    convert_key(key): convert_value(key, value) if value[0] else "" for key, value in bucket.items()
                }
                return GetBucketMeta(**converted_data_list["bucket"])

        return GetBucketMeta()
