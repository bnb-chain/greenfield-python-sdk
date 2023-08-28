import pytest

from greenfield_python_sdk import BlockchainClient
from greenfield_python_sdk.blockchain._cosmos.bank import QueryBalanceRequest
from greenfield_python_sdk.config import NetworkConfiguration, NetworkTestnet

testnet_configuration = NetworkConfiguration(**NetworkTestnet().model_dump())


@pytest.mark.asyncio
async def test_blockchain_client():
    async with BlockchainClient(testnet_configuration) as client:
        # Get bridge parameters
        bridge_params = await client.bridge.get_params()
        print(f"Bridge Parameters: {bridge_params}")
        assert bridge_params

        # Get payment parameters
        payment_params = await client.payment.get_params()
        print(f"Payment Parameters: {payment_params}")
        assert payment_params

        # Get challenge parameters
        latest_attested_challenge = await client.challenge.get_latest_attested_challenges()
        print(f"Challenge latest_attested_challenge: {latest_attested_challenge}")
        assert latest_attested_challenge is not None

        # Get permission parameters
        permission_params = await client.permission.get_params()
        print(f"Permission Parameters: {permission_params}")
        assert permission_params

        # Get SP parameters
        sp_params = await client.sp.get_params()
        print(f"SP Parameters: {sp_params}")
        assert sp_params

        # Get storage parameters
        storage_params = await client.storage.get_params()
        print(f"Storage Parameters: {storage_params}")
        assert storage_params

        # Get address balance using cosmos bank
        balance = await client.cosmos.bank.get_balance(
            QueryBalanceRequest("0xf423fbbf4dcd9fe630e60d4be6e8b13a27cb734b", "BNB")
        )
        print(f"Balance: {balance}")
        assert balance

        # Get node info
        info = await client.tendermint.get_node_info()
        print(f"Info: {info}")
        assert info
