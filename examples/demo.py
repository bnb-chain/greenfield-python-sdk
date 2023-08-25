import asyncio
import io

from greenfield_python_sdk.config import NetworkConfiguration, NetworkTestnet, get_account_configuration
from greenfield_python_sdk.greenfield_client import GreenfieldClient
from greenfield_python_sdk.key_manager import KeyManager
from greenfield_python_sdk.models.bucket import CreateBucketOptions
from greenfield_python_sdk.models.object import CreateObjectOptions, PutObjectOptions
from greenfield_python_sdk.protos.greenfield.storage import VisibilityType

config = get_account_configuration()


async def main():
    network_configuration = NetworkConfiguration(**NetworkTestnet().model_dump())
    key_manager = KeyManager(private_key=config.private_key)
    
    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        await client.async_init()

        bucket_name = "demobucket"
        object_name = "demoimage.png"

        # Get a Storage Provider
        sp = await client.blockchain_client.sp.get_first_in_service_storage_provider()

        # Create Bucket
        tx_hash = await client.bucket.create_bucket(
            bucket_name,
            primary_sp_address=sp["operator_address"],
            opts=CreateBucketOptions(charged_read_quota=100, visibility=VisibilityType.VISIBILITY_TYPE_PRIVATE),
        )
        await client.basic.wait_for_tx(hash=tx_hash)

        # Create Object
        with open('./examples/img.png', 'rb') as f:
            file = f.read()
        content = io.BytesIO(file)

        tx_hash = await client.object.create_object(
            bucket_name,
            object_name,
            reader=content,
            opts=CreateObjectOptions(content_type="image/png"),
        )
        await client.basic.wait_for_tx(hash=tx_hash)
        
        # Put Object
        await client.object.put_object(
            bucket_name=bucket_name,
            object_name=object_name,
            object_size=content.getbuffer().nbytes,
            reader=content.getvalue(),
            opts=PutObjectOptions(content_type="image/png")
        )

        breakpoint() # View the object in the explorer https://dcellar.io/

        # Delete Object
        tx_hash = await client.object.delete_object(
            bucket_name=bucket_name,
            object_name=object_name,
        )
        await client.basic.wait_for_tx(hash=tx_hash)

        # Delete Bucket
        tx_hash = await client.bucket.delete_bucket(
            bucket_name=bucket_name
        )
        await client.basic.wait_for_tx(hash=tx_hash)


if __name__ == "__main__":
    asyncio.run(main())
