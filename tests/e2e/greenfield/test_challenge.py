import asyncio
import random
import string

import pytest

from greenfield_python_sdk import (
    GreenfieldClient,
    KeyManager,
    NetworkConfiguration,
    NetworkLocalnet,
    NetworkTestnet,
    get_account_configuration,
)
from greenfield_python_sdk.models.bucket import CreateBucketOptions
from greenfield_python_sdk.models.object import CreateObjectOptions, PutObjectOptions
from greenfield_python_sdk.protos.greenfield.challenge import AttestedChallenge, QueryInturnAttestationSubmitterResponse
from greenfield_python_sdk.protos.greenfield.sp import QueryStorageProvidersRequest
from greenfield_python_sdk.protos.greenfield.storage import VisibilityType
from greenfield_python_sdk.storage_provider.utils import create_example_object

pytestmark = [pytest.mark.asyncio, pytest.mark.e2e]


# Initialize the configuration, key manager
network_configuration = NetworkConfiguration(**NetworkTestnet().model_dump())
key_manager = KeyManager()


@pytest.mark.requires_config
@pytest.mark.tx
@pytest.mark.slow
@pytest.mark.go_library
async def test_submit_challenge():
    config = get_account_configuration()
    key_manager = KeyManager(private_key=config.private_key)

    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        await client.async_init()
        bucket_name = "".join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(5, 11)))
        object_name = "".join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(5, 11)))
        random_index = False
        segment_index = 0
        content = create_example_object()

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
            content,
            opts=CreateObjectOptions(),
        )
        assert tx_hash
        assert len(tx_hash) == 64
        assert isinstance(tx_hash, str)
        await client.basic.wait_for_tx(hash=tx_hash)

        put_object = await client.object.put_object(
            bucket_name,
            object_name,
            content.getbuffer().nbytes,
            content.getvalue(),
            opts=PutObjectOptions(),
        )
        assert put_object == "Object added successfully"

        await asyncio.sleep(8)
        tx_hash = await client.challenge.submit_challenge(
            key_manager.address,
            sps[0].operator_address,
            bucket_name,
            object_name,
            random_index,
            segment_index,
        )
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


async def test_get_latest_attested_challenges():
    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        response = await client.challenge.get_latest_attested_challenges()
        assert response
        assert isinstance(response, list)
        assert isinstance(response[0], AttestedChallenge)


async def test_get_inturn_attestation_submitter():
    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        response = await client.challenge.get_inturn_attestation_submitter()
        assert response
        assert isinstance(response, QueryInturnAttestationSubmitterResponse)


async def test_get_challenge_params():
    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        response = await client.challenge.get_challenge_params()
        assert response
