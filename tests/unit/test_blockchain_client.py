import pytest

from greenfield_python_sdk import BlockchainClient
from greenfield_python_sdk.blockchain.bridge import Bridge
from greenfield_python_sdk.blockchain.challenge import Challenge
from greenfield_python_sdk.blockchain.cosmos import Cosmos
from greenfield_python_sdk.blockchain.payment import Payment
from greenfield_python_sdk.blockchain.permission import Permission
from greenfield_python_sdk.blockchain.sp import Sp
from greenfield_python_sdk.blockchain.storage import Storage
from greenfield_python_sdk.blockchain.tendermint import Tendermint
from greenfield_python_sdk.config import NetworkConfiguration

HOST = "localhost"
PORT = 9090
CHAIN_ID = 5000

pytestmark = [pytest.mark.unit]


def test_blockchain_client_initialization(mock_channel):
    network_config = NetworkConfiguration(host=HOST, port=PORT, chain_id=CHAIN_ID)
    client = BlockchainClient(network_config, channel=mock_channel)

    assert client.host == HOST
    assert client.port == PORT
    assert client.channel == mock_channel


@pytest.mark.asyncio
async def test_blockchain_context_manager_client_initialization(mock_channel):
    network_config = NetworkConfiguration(host=HOST, port=PORT, chain_id=CHAIN_ID)
    async with BlockchainClient(network_config, channel=mock_channel) as client:
        assert isinstance(client.bridge, Bridge)
        assert isinstance(client.challenge, Challenge)
        assert isinstance(client.payment, Payment)
        assert isinstance(client.permission, Permission)
        assert isinstance(client.sp, Sp)
        assert isinstance(client.storage, Storage)
        assert isinstance(client.cosmos, Cosmos)
        assert isinstance(client.tendermint, Tendermint)


@pytest.mark.asyncio
async def test_blockchain_client_connected(mock_channel):
    network_config = NetworkConfiguration(host=HOST, port=PORT, chain_id=CHAIN_ID)
    mock_channel._connected = True
    client = BlockchainClient(network_config, channel=mock_channel)

    assert client.connected is True


@pytest.mark.asyncio
async def test_blockchain_client_not_connected(mock_channel):
    network_config = NetworkConfiguration(host=HOST, port=PORT, chain_id=CHAIN_ID)
    mock_channel._connected = False
    client = BlockchainClient(network_config, channel=mock_channel)

    assert client.connected is False
