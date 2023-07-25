import asyncio
import logging
import random
import string

from betterproto import Casing

from greenfield_python_sdk.blockchain.utils import parse_account
from greenfield_python_sdk.blockchain_client import BlockchainClient
from greenfield_python_sdk.config import NetworkConfiguration, get_account_configuration
from greenfield_python_sdk.key_manager import KeyManager
from greenfield_python_sdk.models.bucket import CreateBucketOptions, ListReadRecordOptions
from greenfield_python_sdk.models.eip712_messages.storage.bucket_url import CREATE_BUCKET, DELETE_BUCKET
from greenfield_python_sdk.models.eip712_messages.storage.object_url import CREATE_OBJECT, DELETE_OBJECT
from greenfield_python_sdk.models.object import (
    CreateObjectOptions,
    GetObjectOption,
    ListObjectsOptions,
    PutObjectOptions,
)
from greenfield_python_sdk.models.transaction import BroadcastOption
from greenfield_python_sdk.protos.cosmos.auth.v1beta1 import QueryAccountRequest
from greenfield_python_sdk.protos.greenfield.storage import (
    MsgDeleteBucket,
    MsgDeleteObject,
    QueryHeadBucketRequest,
    VisibilityType,
)
from greenfield_python_sdk.storage_client import StorageClient
from greenfield_python_sdk.storage_provider.utils import create_example_object

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

config = get_account_configuration()


async def main():
    network_configuration = NetworkConfiguration()
    key_manager = KeyManager(private_key=config.private_key)

    logger.info(f"Main account address: {key_manager.address}")

    async with BlockchainClient(network_configuration=network_configuration, key_manager=key_manager) as blockchain_client:
        response = await blockchain_client.cosmos.auth.get_account(QueryAccountRequest(address=key_manager.address))
        account = await parse_account(response)
        
        key_manager.account.next_sequence = account.sequence
        key_manager.account.account_number = account.account_number

        response = await blockchain_client.sp.get_storage_providers()
        sp_endpoints = {sp["operatorAddress"]:sp for sp in response.to_pydict()["sps"]} # Transform the response to a dict with the operatorAddress as key
        sp_address = list(sp_endpoints.keys())[0]
        async with StorageClient(key_manager=key_manager, sp_endpoints=sp_endpoints) as client:
            bucket_name = "".join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(5, 11)))
            object_name = "".join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(5, 11)))

            logger.info(f"---> Get Bucket Approval <---")
            bucket_approval, sp_signature = await client.bucket.get_bucket_approval(
                bucket_name=bucket_name,
                primary_sp_address=sp_address,
                opts=CreateBucketOptions(charged_read_quota=100, visibility=VisibilityType.VISIBILITY_TYPE_PRIVATE),
            )
            logger.info(f"Response:\n - Bucket Approval: {bucket_approval}\n - SP Signature: {sp_signature}\n\n")
            
            ## Create the Bucket
            await blockchain_client.broadcast_message(
                message=bucket_approval, type_url=CREATE_BUCKET, broadcast_option=BroadcastOption(sp_signature=sp_signature)
            )
            await asyncio.sleep(5)

            # logger.info(f"---> List Buckets <---")
            # list_bucket = await client.bucket.list_buckets(sp_address=sp_address)
            # logger.info(f"Response: {list_bucket}\n\n")

            logger.info(f"---> Bucket Read Quota <---")
            response = await blockchain_client.storage.get_head_bucket(QueryHeadBucketRequest(bucket_name=bucket_name))
            primary_sp_address = response.to_pydict(casing=Casing.SNAKE)["bucket_info"]["primary_sp_address"]
            quota = await client.bucket.get_bucket_read_quota(
                bucket_name=bucket_name,
                primary_sp_address=primary_sp_address
            )
            logger.info(f"Response: {quota}\n\n")
            

            logger.info(f"---> bucket read record <---")
            response = await blockchain_client.storage.get_head_bucket(QueryHeadBucketRequest(bucket_name=bucket_name))
            primary_sp_address = response.to_pydict(casing=Casing.SNAKE)["bucket_info"]["primary_sp_address"]
            bucket_read_record = await client.bucket.list_bucket_read_record(
                bucket_name=bucket_name,
                primary_sp_address=primary_sp_address,
                opts=ListReadRecordOptions(
                    max_records=10
                )
            )
            logger.info(f"Response: {bucket_read_record}\n\n")

            content = create_example_object()
            logger.info(f"---> Get Object Approval <---")
            response = await blockchain_client.storage.get_head_bucket(QueryHeadBucketRequest(bucket_name=bucket_name))
            primary_sp_address = response.to_pydict(casing=Casing.SNAKE)["bucket_info"]["primary_sp_address"]
            storage_params = await blockchain_client.storage.get_params()
            object_approval, sp_signature, checksums= await client.object.get_object_approval(
                bucket_name=bucket_name,
                object_name=object_name,
                opts=CreateObjectOptions(),
                primary_sp_address=primary_sp_address,
                reader=content,
                storage_params=storage_params,
            )
            logger.info(f"Response:\n - Object Approval: {object_approval}\n - Storage Provider signature: {sp_signature}\n - Checksums: {checksums} \n\n")

            ## Create the Object
            await blockchain_client.broadcast_message(
                message=object_approval,
                type_url=CREATE_OBJECT,
                broadcast_option=BroadcastOption(sp_signature=sp_signature, checksums=checksums),
            )
            await asyncio.sleep(5)

            logger.info(f"---> Put Object <---")
            response = await blockchain_client.storage.get_head_bucket(QueryHeadBucketRequest(bucket_name=bucket_name))
            primary_sp_address = response.to_pydict(casing=Casing.SNAKE)["bucket_info"]["primary_sp_address"]
            put_object = await client.object.put_object(
                bucket_name=bucket_name,
                object_name=object_name,
                object_size=content.getbuffer().nbytes,
                primary_sp_address=primary_sp_address,
                reader=content.getvalue(),
                opts=PutObjectOptions(),
            )
            logger.info(f"Response: {put_object}\n\n")
            await asyncio.sleep(5)

   
            logger.info(f"---> Get Object <---")
            response = await blockchain_client.storage.get_head_bucket(QueryHeadBucketRequest(bucket_name=bucket_name))
            primary_sp_address = response.to_pydict(casing=Casing.SNAKE)["bucket_info"]["primary_sp_address"]
        
            info, object_data = await client.object.get_object(
                bucket_name=bucket_name,
                object_name=object_name,
                opts=GetObjectOption(),
                primary_sp_address=primary_sp_address
            )
            logger.info(f"Response:\n - Info: {info}\n - Object data: {object_data}\n\n")
         

            logger.info(f"---> Get list Object <---")
            response = await blockchain_client.storage.get_head_bucket(QueryHeadBucketRequest(bucket_name=bucket_name))
            primary_sp_address = response.to_pydict(casing=Casing.SNAKE)["bucket_info"]["primary_sp_address"]
            list_objects = await client.object.list_objects(
                bucket_name=bucket_name,
                opts=ListObjectsOptions(),
                primary_sp_address=primary_sp_address
            )
            logger.info(f"Response: {list_objects}\n\n")

            logger.info(f"---> Remove Bucket and Object <---")
            ## Delete the Object
            delete_object_msg = MsgDeleteObject(
                operator=key_manager.address, bucket_name=bucket_name, object_name=object_name
            )
            await blockchain_client.broadcast_message(message=delete_object_msg, type_url=DELETE_OBJECT)
            await asyncio.sleep(5)

            ## Delete the Bucket
            delete_bucket_msg = MsgDeleteBucket(operator=key_manager.address, bucket_name=bucket_name)
            await blockchain_client.broadcast_message(message=delete_bucket_msg, type_url=DELETE_BUCKET)
            await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(main())
