from random import randint

import pytest

from greenfield_python_sdk import (
    GreenfieldClient,
    KeyManager,
    NetworkConfiguration,
    NetworkTestnet,
    get_account_configuration,
)
from greenfield_python_sdk.blockchain._cosmos.oracle import QueryInturnRelayerResponse
from greenfield_python_sdk.greenfield.account import Coin

pytestmark = [pytest.mark.asyncio, pytest.mark.e2e]


# Initialize the configuration, key manager
network_configuration = NetworkConfiguration(**NetworkTestnet().model_dump())
key_manager = KeyManager()


@pytest.mark.requires_config
@pytest.mark.tx
@pytest.mark.slow
async def test_transfer_out():
    config = get_account_configuration()
    key_manager = KeyManager(private_key=config.private_key)

    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        await client.async_init()

        tx_hash = await client.crosschain.transfer_out(
            to_address=key_manager.address, amount=Coin(denom="BNB", amount="1000000000")
        )

        assert tx_hash
        assert isinstance(tx_hash, str)
        await client.basic.wait_for_tx(tx_hash)


async def test_get_channel_send_sequence():
    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        sequence = await client.crosschain.get_channel_send_sequence(1)
        assert isinstance(sequence, int)


async def test_get_channel_receive_sequence():
    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        sequence = await client.crosschain.get_channel_receive_sequence(1)
        assert isinstance(sequence, int)


async def test_get_inturn_relayer():
    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        response = await client.crosschain.get_inturn_relayer()
        assert response
        assert isinstance(response, QueryInturnRelayerResponse)


async def test_get_crosschain_package():
    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        package = await client.crosschain.get_crosschain_package(channel_id=1, sequence=0)
        assert package
        assert isinstance(package, bytes)


@pytest.mark.requires_config
@pytest.mark.tx
@pytest.mark.slow
async def test_mirror_group():
    config = get_account_configuration()
    key_manager = KeyManager(private_key=config.private_key)

    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        await client.async_init()

        with pytest.raises(Exception):
            tx_hash = await client.crosschain.mirror_group(group_id="1", group_name="")
            assert tx_hash
            assert isinstance(tx_hash, str)
            await client.basic.wait_for_tx(hash=tx_hash)
            # TODO: add create group and mirror that group


@pytest.mark.requires_config
@pytest.mark.tx
@pytest.mark.slow
async def test_mirror_bucket():
    config = get_account_configuration()
    key_manager = KeyManager(private_key=config.private_key)

    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        await client.async_init()

        with pytest.raises(Exception):
            tx_hash = await client.crosschain.mirror_bucket(
                bucket_id=f"{randint(1000, 10000)}", bucket_name=f"{randint(1000, 10000)}"
            )
            assert tx_hash
            assert isinstance(tx_hash, str)
            await client.basic.wait_for_tx(hash=tx_hash)
            # TODO: add create bucket and mirror that bucket


@pytest.mark.requires_config
@pytest.mark.tx
@pytest.mark.slow
async def test_mirror_object():
    config = get_account_configuration()
    key_manager = KeyManager(private_key=config.private_key)

    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        await client.async_init()

        with pytest.raises(Exception):
            tx_hash = await client.crosschain.mirror_object(
                object_id=f"{randint(1000, 10000)}",
                bucket_name=f"{randint(1000, 10000)}",
                object_name=f"{randint(1000, 10000)}",
            )
            assert tx_hash
            assert isinstance(tx_hash, str)
            await client.basic.wait_for_tx(hash=tx_hash)
            # TODO: add create object and mirror that object
