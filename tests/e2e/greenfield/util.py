from greenfield_python_sdk import (
    GreenfieldClient,
    KeyManager,
    NetworkConfiguration,
    NetworkTestnet,
    get_account_configuration,
)
from greenfield_python_sdk.models.object import ListObjectsOptions

network_configuration = NetworkConfiguration(**NetworkTestnet().model_dump())
principal_key_manager = KeyManager()


async def cleanup():
    config = get_account_configuration()
    key_manager = KeyManager(private_key=config.private_key)
    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        await client.async_init()
        sp = (await client.blockchain_client.get_active_sps())[0]

        bucket_list = await client.bucket.list_buckets(sp["operator_address"])
        buckets = [bucket.bucket_info.bucket_name for bucket in bucket_list]
        for bucket_name in buckets:
            list_object = await client.object.list_objects(bucket_name, ListObjectsOptions())

            for object_name in list_object.objects:
                tx_hash = await client.object.delete_object(
                    bucket_name,
                    object_name,
                )
                assert tx_hash
                await client.basic.wait_for_tx(hash=tx_hash)

            tx_hash = await client.bucket.delete_bucket(bucket_name)
            assert tx_hash
            await client.basic.wait_for_tx(hash=tx_hash)
