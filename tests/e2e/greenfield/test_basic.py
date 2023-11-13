import pytest

from greenfield_python_sdk import (
    GreenfieldClient,
    KeyManager,
    NetworkConfiguration,
    NetworkTestnet,
    get_account_configuration,
)
from greenfield_python_sdk.greenfield.account import Coin
from greenfield_python_sdk.models.basic import ResultBlockResults, ResultCommit, ResultStatus
from greenfield_python_sdk.protos.cosmos.bank.v1beta1 import MsgSend
from greenfield_python_sdk.protos.cosmos.base.query.v1beta1 import PageResponse as PaginationResponse
from greenfield_python_sdk.protos.cosmos.base.tendermint.v1beta1 import (
    GetBlockByHeightResponse,
    GetLatestBlockResponse,
    GetNodeInfoResponse,
    Validator,
)
from greenfield_python_sdk.protos.cosmos.tx.v1beta1 import SimulateResponse

pytestmark = [pytest.mark.asyncio, pytest.mark.e2e]


# Initialize the configuration, key manager
network_configuration = NetworkConfiguration(**NetworkTestnet().model_dump())
key_manager = KeyManager()


async def test_get_node_info():
    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        response = await client.basic.get_node_info()
        assert response
        assert isinstance(response, GetNodeInfoResponse)


async def test_get_latest_block_height():
    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        response = await client.basic.get_latest_block_height()
        assert response
        assert isinstance(response, int)


async def test_get_latest_block():
    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        response = await client.basic.get_latest_block()
        assert response
        assert isinstance(response, GetLatestBlockResponse)


async def test_get_syncing():
    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        response = await client.basic.get_syncing()
        assert isinstance(response, bool)


async def test_get_block_by_height():
    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        height = 1
        response = await client.basic.get_block_by_height(height=height)
        assert response
        assert isinstance(response, GetBlockByHeightResponse)


async def test_get_validator_set():
    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        block_height, validators = await client.basic.get_validator_set()
        assert validators
        assert isinstance(validators, list)
        assert isinstance(validators[0], Validator)
        assert isinstance(block_height, int)


async def test_get_status():
    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        response = await client.basic.get_status()
        assert response
        assert isinstance(response, ResultStatus)


async def test_get_commit():
    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        response = await client.basic.get_commit(height=1)
        assert response
        assert isinstance(response, ResultCommit)


async def test_get_block_result_by_height():
    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        response = await client.basic.get_block_result_by_height(height=1)
        assert response
        assert isinstance(response, ResultBlockResults)


async def test_get_validators_by_height():
    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        response = await client.basic.get_validators_by_height(height=1)
        assert response
        assert isinstance(response, list)
        assert isinstance(response[0], Validator)


@pytest.mark.slow
async def test_wait_for_block_height():
    # Depends on get_latest_block_height
    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        latest_block = await client.basic.get_latest_block_height()
        assert latest_block
        target_block = latest_block + 1

        response = await client.basic.wait_for_block_height(height=target_block)
        assert response
        assert isinstance(response, int)
        assert response == target_block


@pytest.mark.requires_config
@pytest.mark.tx
@pytest.mark.slow
async def test_wait_for_tx():
    # Depends on account.transfer
    config = get_account_configuration()
    key_manager = KeyManager(private_key=config.private_key)

    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        await client.async_init()

        secondary_key_manager = KeyManager()  # Create a new account for the transfer
        hash = await client.account.transfer(
            from_address=key_manager.address,
            to_address=secondary_key_manager.address,
            amounts=[Coin(denom="BNB", amount="1")],
        )
        assert hash

        response = await client.basic.wait_for_tx(hash=hash)
        assert response


@pytest.mark.slow
async def test_wait_for_n_blocks():
    # Depends on get_latest_block_height and wait_for_block_height
    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        n = 2
        initial_block = await client.basic.get_latest_block_height()
        response = await client.basic.wait_for_n_blocks(n=n)
        assert response
        assert isinstance(response, int)
        assert response in [initial_block + n, initial_block + n + 1]


@pytest.mark.slow
async def test_wait_for_next_block():
    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        initial_block = await client.basic.get_latest_block_height()
        response = await client.basic.wait_for_next_block()
        assert response
        assert isinstance(response, int)
        assert response in [initial_block + 1, initial_block + 2]


@pytest.mark.requires_config
@pytest.mark.tx
@pytest.mark.slow
async def test_simulate_tx():
    config = get_account_configuration()
    key_manager = KeyManager(private_key=config.private_key)

    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        await client.async_init()

        secondary_key_manager = KeyManager()  # Create a new account for the transfer

        message = MsgSend(
            from_address=key_manager.address,
            to_address=secondary_key_manager.address,
            amount=[Coin(denom="BNB", amount="1")],
        )

        tx = await client.blockchain_client.build_tx_from_message(
            message=message, type_url="/cosmos.bank.v1beta1.MsgSend"
        )

        response = await client.basic.simulate_tx(tx=tx)
        assert response
        assert isinstance(response, SimulateResponse)


@pytest.mark.requires_config
@pytest.mark.tx
@pytest.mark.slow
async def test_simulate_raw_tx():
    config = get_account_configuration()
    key_manager = KeyManager(private_key=config.private_key)

    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        await client.async_init()

        secondary_key_manager = KeyManager()  # Create a new account for the transfer

        message = MsgSend(
            from_address=key_manager.address,
            to_address=secondary_key_manager.address,
            amount=[Coin(denom="BNB", amount="1")],
        )

        tx = await client.blockchain_client.build_tx_from_message(
            message=message, type_url="/cosmos.bank.v1beta1.MsgSend"
        )

        response = await client.basic.simulate_raw_tx(tx_bytes=bytes(tx))
        assert response
        assert isinstance(response, SimulateResponse)


@pytest.mark.requires_config
@pytest.mark.tx
@pytest.mark.slow
async def test_broadcast_tx():
    config = get_account_configuration()
    key_manager = KeyManager(private_key=config.private_key)

    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        await client.async_init()

        secondary_key_manager = KeyManager()  # Create a new account for the transfer

        message = MsgSend(
            from_address=key_manager.address,
            to_address=secondary_key_manager.address,
            amount=[Coin(denom="BNB", amount="1")],
        )

        tx = await client.blockchain_client.build_tx_from_message(
            message=message, type_url="/cosmos.bank.v1beta1.MsgSend"
        )

        response = await client.basic.broadcast_tx(tx=tx)
        assert response
        assert isinstance(response, str)

        await client.basic.wait_for_tx(hash=response)


@pytest.mark.requires_config
@pytest.mark.tx
@pytest.mark.slow
async def test_broadcast_raw_tx():
    config = get_account_configuration()
    key_manager = KeyManager(private_key=config.private_key)

    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        await client.async_init()

        secondary_key_manager = KeyManager()  # Create a new account for the transfer

        message = MsgSend(
            from_address=key_manager.address,
            to_address=secondary_key_manager.address,
            amount=[Coin(denom="BNB", amount="1")],
        )

        tx = await client.blockchain_client.build_tx_from_message(
            message=message, type_url="/cosmos.bank.v1beta1.MsgSend"
        )

        response = await client.basic.broadcast_raw_tx(tx_bytes=bytes(tx))
        assert response
        assert isinstance(response, str)

        await client.basic.wait_for_tx(hash=response)
