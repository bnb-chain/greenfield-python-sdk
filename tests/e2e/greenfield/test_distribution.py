import pytest

from greenfield_python_sdk import GreenfieldClient, KeyManager, NetworkConfiguration, get_account_configuration

pytestmark = [pytest.mark.asyncio, pytest.mark.e2e]


# Initialize the configuration, key manager
network_configuration = NetworkConfiguration()
key_manager = KeyManager()


@pytest.mark.requires_config
@pytest.mark.tx
@pytest.mark.slow
async def test_set_withdraw_address():
    config = get_account_configuration()
    key_manager = KeyManager(private_key=config.private_key)

    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        await client.async_init()

        secondary_key_manager = KeyManager()  # Create a new account
        hash = await client.distribution.set_withdraw_address(
            withdraw_address=secondary_key_manager.address,
        )
        assert hash
        assert isinstance(hash, str)
        await client.basic.wait_for_tx(hash=hash)


@pytest.mark.requires_config
@pytest.mark.tx
@pytest.mark.slow
async def test_withdraw_validator_commission_failed():
    # This call will raise an exception because the account has no validator commission to withdraw
    config = get_account_configuration()
    key_manager = KeyManager(private_key=config.private_key)

    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        await client.async_init()

        with pytest.raises(Exception) as excinfo:
            await client.distribution.withdraw_validator_commission(
                validator_address=key_manager.address,
            )
        assert "failed to execute message; message index: 0: no validator commission to withdraw" in str(excinfo.value)


@pytest.mark.requires_config
@pytest.mark.tx
@pytest.mark.slow
async def test_withdraw_delegator_reward_failed():
    # This call will raise an exception because the account has no validator distribution info
    config = get_account_configuration()
    key_manager = KeyManager(private_key=config.private_key)

    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        await client.async_init()

        response = await client.validator.list_validators()
        assert response

        with pytest.raises(Exception) as excinfo:
            await client.distribution.withdraw_delegator_reward(
                validator_address=response.validators[1].operator_address,
            )

        assert "failed to execute message; message index: 0: no validator distribution info" in str(excinfo.value)


@pytest.mark.requires_config
@pytest.mark.tx
@pytest.mark.slow
async def test_fund_community_pool_failed():
    # This call will raise an exception because internally it seems that the message type is not recognized
    config = get_account_configuration()
    key_manager = KeyManager(private_key=config.private_key)

    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        await client.async_init()

        with pytest.raises(Exception) as excinfo:
            await client.distribution.fund_community_pool(
                amount=1,
            )

        assert "unrecognized msg type: /cosmos.distribution.v1beta1.MsgFundCommunityPool" in str(excinfo.value)
