import asyncio
import logging
import random
import string

from greenfield_python_sdk.config import NetworkConfiguration, NetworkTestnet, get_account_configuration
from greenfield_python_sdk.greenfield_client import GreenfieldClient
from greenfield_python_sdk.key_manager import KeyManager
from greenfield_python_sdk.models.bucket import CreateBucketOptions
from greenfield_python_sdk.models.object import CreateObjectOptions, GetObjectOption, PutObjectOptions
from greenfield_python_sdk.protos.greenfield.sp import QueryStorageProvidersRequest
from greenfield_python_sdk.protos.greenfield.storage import VisibilityType
from greenfield_python_sdk.storage_provider.utils import create_example_object

logging.basicConfig(level=logging.INFO)

config = get_account_configuration()


async def main():
    network_configuration = NetworkConfiguration(**NetworkTestnet().model_dump())
    key_manager = KeyManager(private_key=config.private_key)

    logging.info(f"Main account address: {key_manager.address}")
    
    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        logging.info(f"---> TEST Greenfield <---")
        bucket_name = "".join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(5, 11)))
        object_name = "".join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(5, 11)))
        await client.async_init()

        ## Get Storage Providers
        sps = (await client.blockchain_client.sp.get_storage_providers(QueryStorageProvidersRequest())).sps

        logging.info(f"---> Create Bucket <---")
        create_bucket = await client.bucket.create_bucket(
            bucket_name,
            primary_sp_address=sps[0].operator_address,
            opts=CreateBucketOptions(charged_read_quota=100, visibility=VisibilityType.VISIBILITY_TYPE_PRIVATE),
        )
        logging.info(f"Result: {create_bucket}\n\n")
        await client.basic.wait_for_tx(hash=create_bucket)

        ## Create Object
        content = create_example_object()

        logging.info(f"---> Create Object <---")
        object = await client.object.create_object(
            bucket_name,
            object_name,
            reader=content,
            opts=CreateObjectOptions()
        )
        logging.info(f"Result: {object}\n\n")
        await client.basic.wait_for_tx(hash=object)

        logging.info(f"---> Put Object <---")
        put_object = await client.object.put_object(
            bucket_name,
            object_name,
            object_size=content.getbuffer().nbytes,
            reader=content.getvalue(),
            opts=PutObjectOptions()
        )
        logging.info(f"Result: {put_object}\n\n")

        await asyncio.sleep(8)

        logging.info(f"---> Get Object <---")
        get_object = await client.object.get_object(
            bucket_name,
            object_name,
            opts=GetObjectOption()
        )
        logging.info(f"Result: {get_object}\n\n")

        logging.info(f"---> Delete Object <---")
        delete_object = await client.object.delete_object(
            bucket_name,
            object_name,
        )
        logging.info(f"Result: {delete_object}\n\n")
        await client.basic.wait_for_tx(hash=delete_object)

        logging.info(f"---> Delete Bucket <---")
        delete_bucket = await client.bucket.delete_bucket(
            bucket_name=bucket_name,
        )
        logging.info(f"Result: {delete_bucket}\n\n")


if __name__ == "__main__":
    asyncio.run(main())
