from datetime import datetime, timedelta

import pytest

from greenfield_python_sdk import (
    GreenfieldClient,
    KeyManager,
    NetworkConfiguration,
    NetworkTestnet,
    get_account_configuration,
)
from greenfield_python_sdk.greenfield.account import Coin
from greenfield_python_sdk.protos.cosmos.feegrant.v1beta1 import BasicAllowance, Grant
from greenfield_python_sdk.protos.cosmos.tx.v1beta1 import Fee

ALLOWANCE_LIMIT = 1200000000000000


pytestmark = [pytest.mark.asyncio, pytest.mark.e2e]


# Initialize the configuration, key manager
network_configuration = NetworkConfiguration(**NetworkTestnet().model_dump())
key_manager = KeyManager()


@pytest.mark.requires_config
@pytest.mark.tx
@pytest.mark.slow
@pytest.mark.funds
async def test_grant_basic_allowance():
    # Depends on account.transfer
    config = get_account_configuration()
    key_manager = KeyManager(private_key=config.private_key)

    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        await client.async_init()

        # Create a new account for the granter, this account will grant the allowance
        granter_key_manager = KeyManager()

        # Create a new account for the grantee, this account will receive the allowance
        grantee_key_manager = KeyManager()

        # Fund both accounts with a transaction with the base account
        # Granter
        hash = await client.account.transfer(
            from_address=key_manager.address,
            to_address=granter_key_manager.address,
            amounts=[Coin(denom="BNB", amount="1400000000000000")],
        )
        assert hash
        await client.basic.wait_for_tx(hash)

        # Grantee
        hash = await client.account.transfer(
            from_address=key_manager.address,
            to_address=grantee_key_manager.address,
            amounts=[Coin(denom="BNB", amount="1400000000000000")],
        )
        assert hash
        assert isinstance(hash, str)
        await client.basic.wait_for_tx(hash)

        # Granter grants allowance to grantee
        await client.set_default_account(granter_key_manager.account)

        hash = await client.feegrant.grant_basic_allowance(
            grantee_address=grantee_key_manager.address,
            spend_limit=ALLOWANCE_LIMIT,
            expiration=datetime.now() + timedelta(days=5),
        )
        assert hash
        assert isinstance(hash, str)
        await client.basic.wait_for_tx(hash)

        # Query the allowance from granter to grantee
        allowance = await client.feegrant.get_basic_allowance(
            granter_address=granter_key_manager.address,
            grantee_address=grantee_key_manager.address,
        )
        assert allowance
        assert isinstance(allowance, BasicAllowance)
        assert int(allowance.spend_limit[0].amount) == ALLOWANCE_LIMIT

        # Show grantee balance before the grantee making a tx
        initial_balance = await client.account.get_account_balance(address=grantee_key_manager.address)
        assert isinstance(initial_balance, int)

        # Grantee makes a tx and costs the fee provided by granter
        await client.set_default_account(grantee_key_manager.account)

        fee = Fee(
            amount=[Coin(amount="10000000000000", denom="BNB")],
            gas_limit=2000,
            granter=granter_key_manager.address,
            payer=grantee_key_manager.address,
        )

        hash = await client.account.create_payment_account(address=grantee_key_manager.address, fee=fee)
        assert hash
        assert isinstance(hash, str)
        await client.basic.wait_for_tx(hash)

        final_balance = await client.account.get_account_balance(address=grantee_key_manager.address)
        assert isinstance(final_balance, int)

        granter_balance = await client.account.get_account_balance(address=granter_key_manager.address)
        assert isinstance(granter_balance, int)

        # Granter balance is reduced because the granter paid the fees
        assert granter_balance < initial_balance

        # Grantee balance is the same
        assert final_balance == initial_balance

        # Query the allowance from granter to grantee again, it should be reduced
        allowance_after = await client.feegrant.get_basic_allowance(
            granter_address=granter_key_manager.address,
            grantee_address=grantee_key_manager.address,
        )

        assert allowance_after
        assert isinstance(allowance_after, BasicAllowance)
        assert int(allowance_after.spend_limit[0].amount) < ALLOWANCE_LIMIT

        # The granter revokes the allowance
        await client.set_default_account(granter_key_manager.account)

        hash = await client.feegrant.revoke_allowance(
            granter_address=granter_key_manager.address,
            grantee_address=grantee_key_manager.address,
        )
        assert hash
        assert isinstance(hash, str)
        await client.basic.wait_for_tx(hash)

        # Query the allowance from the granter to the grantee, must raise exception
        with pytest.raises(Exception):
            await client.feegrant.get_basic_allowance(
                granter_address=granter_key_manager.address,
                grantee_address=grantee_key_manager.address,
            )

        # Make another transaction, it should fail as well
        await client.set_default_account(grantee_key_manager.account)

        fee = Fee(
            amount=[Coin(denom="BNB", amount="10000000000000")],
            gas_limit=2000,
            granter=granter_key_manager.address,
            payer=grantee_key_manager.address,
        )

        with pytest.raises(Exception):
            await client.account.create_payment_account(address=grantee_key_manager.address, fee=fee)


@pytest.mark.requires_config
@pytest.mark.tx
@pytest.mark.slow
@pytest.mark.funds
async def test_grant_allowance():
    # Depends on account.transfer
    config = get_account_configuration()
    key_manager = KeyManager(private_key=config.private_key)

    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        await client.async_init()

        # Create a new account for the granter, this account will grant the allowance
        granter_key_manager = KeyManager()

        # Create a new account for the grantee, this account will receive the allowance
        grantee_key_manager = KeyManager()

        # Fund both accounts with a transaction with the base account
        # Granter
        hash = await client.account.transfer(
            from_address=key_manager.address,
            to_address=granter_key_manager.address,
            amounts=[Coin(denom="BNB", amount="1500000000000000")],
        )
        assert hash
        await client.basic.wait_for_tx(hash)

        # Grantee
        hash = await client.account.transfer(
            from_address=key_manager.address,
            to_address=grantee_key_manager.address,
            amounts=[Coin(denom="BNB", amount="1500000000000000")],
        )
        assert hash
        assert isinstance(hash, str)
        await client.basic.wait_for_tx(hash)

        # Granter grants allowance to grantee
        await client.set_default_account(granter_key_manager.account)

        spend_limit = [Coin(denom="BNB", amount=str(ALLOWANCE_LIMIT))]
        expiration = datetime.now() + timedelta(days=5)
        allowance = BasicAllowance(
            spend_limit=spend_limit,
            expiration=expiration,
        )

        hash = await client.feegrant.grant_allowance(grantee_address=grantee_key_manager.address, allowance=allowance)
        assert hash
        assert isinstance(hash, str)
        await client.basic.wait_for_tx(hash)

        # Query the allowance from granter to grantee
        allowance = await client.feegrant.get_allowance(
            granter_address=granter_key_manager.address,
            grantee_address=grantee_key_manager.address,
        )
        assert allowance
        assert isinstance(allowance, Grant)


@pytest.mark.requires_config
@pytest.mark.tx
@pytest.mark.slow
@pytest.mark.funds
async def test_get_basic_allowance():
    config = get_account_configuration()
    key_manager = KeyManager(private_key=config.private_key)

    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        await client.async_init()

        # Create a new account for the granter, this account will grant the allowance
        granter_key_manager = KeyManager()

        # Create a new account for the grantee, this account will receive the allowance
        grantee_key_manager = KeyManager()

        # Query the allowance from granter to grantee, must raise exception
        with pytest.raises(Exception):
            await client.feegrant.get_basic_allowance(
                granter_address=granter_key_manager.address,
                grantee_address=grantee_key_manager.address,
            )

        # Fund both accounts with a transaction with the base account
        # Granter
        hash = await client.account.transfer(
            from_address=key_manager.address,
            to_address=granter_key_manager.address,
            amounts=[Coin(denom="BNB", amount="1500000000000000")],
        )
        assert hash
        await client.basic.wait_for_tx(hash)

        # Grantee
        hash = await client.account.transfer(
            from_address=key_manager.address,
            to_address=grantee_key_manager.address,
            amounts=[Coin(denom="BNB", amount="1500000000000000")],
        )
        assert hash
        assert isinstance(hash, str)
        await client.basic.wait_for_tx(hash)

        # Granter grants allowance to grantee
        await client.set_default_account(granter_key_manager.account)

        spend_limit = [Coin(denom="BNB", amount=str(ALLOWANCE_LIMIT))]
        expiration = datetime.now() + timedelta(days=5)
        allowance = BasicAllowance(
            spend_limit=spend_limit,
            expiration=expiration,
        )

        hash = await client.feegrant.grant_allowance(grantee_address=grantee_key_manager.address, allowance=allowance)
        assert hash
        assert isinstance(hash, str)
        await client.basic.wait_for_tx(hash)

        # Query the allowance from granter to grantee
        allowance = await client.feegrant.get_basic_allowance(
            granter_address=granter_key_manager.address,
            grantee_address=grantee_key_manager.address,
        )
        assert allowance
        assert isinstance(allowance, BasicAllowance)


@pytest.mark.requires_config
@pytest.mark.tx
@pytest.mark.slow
@pytest.mark.funds
async def test_get_allowance():
    config = get_account_configuration()
    key_manager = KeyManager(private_key=config.private_key)

    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        await client.async_init()

        # Create a new account for the granter, this account will grant the allowance
        granter_key_manager = KeyManager()

        # Create a new account for the grantee, this account will receive the allowance
        grantee_key_manager = KeyManager()

        # Query the allowance from granter to grantee, must raise exception
        with pytest.raises(Exception):
            await client.feegrant.get_allowance(
                granter_address=granter_key_manager.address,
                grantee_address=grantee_key_manager.address,
            )

        # Fund both accounts with a transaction with the base account
        # Granter
        hash = await client.account.transfer(
            from_address=key_manager.address,
            to_address=granter_key_manager.address,
            amounts=[Coin(denom="BNB", amount="1500000000000000")],
        )
        assert hash
        await client.basic.wait_for_tx(hash)

        # Grantee
        hash = await client.account.transfer(
            from_address=key_manager.address,
            to_address=grantee_key_manager.address,
            amounts=[Coin(denom="BNB", amount="1500000000000000")],
        )
        assert hash
        assert isinstance(hash, str)
        await client.basic.wait_for_tx(hash)

        # Granter grants allowance to grantee
        await client.set_default_account(granter_key_manager.account)

        spend_limit = [Coin(denom="BNB", amount=str(ALLOWANCE_LIMIT))]
        expiration = datetime.now() + timedelta(days=5)
        allowance = BasicAllowance(
            spend_limit=spend_limit,
            expiration=expiration,
        )

        hash = await client.feegrant.grant_allowance(grantee_address=grantee_key_manager.address, allowance=allowance)
        assert hash
        assert isinstance(hash, str)
        await client.basic.wait_for_tx(hash)

        # Query the allowance from granter to grantee
        allowance = await client.feegrant.get_allowance(
            granter_address=granter_key_manager.address,
            grantee_address=grantee_key_manager.address,
        )
        assert allowance
        assert isinstance(allowance, Grant)


@pytest.mark.requires_config
@pytest.mark.tx
@pytest.mark.slow
@pytest.mark.funds
async def test_get_allowances():
    config = get_account_configuration()
    key_manager = KeyManager(private_key=config.private_key)

    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        await client.async_init()

        # Create a new account for the granter, this account will grant the allowance
        granter_key_manager = KeyManager()

        # Create a new account for the grantee, this account will receive the allowance
        grantee_key_manager = KeyManager()

        # No allowances
        allowances = await client.feegrant.get_allowances(grantee_address=grantee_key_manager.address)
        assert isinstance(allowances, list)
        assert len(allowances) == 0

        # Fund both accounts with a transaction with the base account
        # Granter
        hash = await client.account.transfer(
            from_address=key_manager.address,
            to_address=granter_key_manager.address,
            amounts=[Coin(denom="BNB", amount="1500000000000000")],
        )
        assert hash
        await client.basic.wait_for_tx(hash)

        # Grantee
        hash = await client.account.transfer(
            from_address=key_manager.address,
            to_address=grantee_key_manager.address,
            amounts=[Coin(denom="BNB", amount="1500000000000000")],
        )
        assert hash
        assert isinstance(hash, str)
        await client.basic.wait_for_tx(hash)

        # Granter grants allowance to grantee
        await client.set_default_account(granter_key_manager.account)

        spend_limit = [Coin(denom="BNB", amount=str(ALLOWANCE_LIMIT))]
        expiration = datetime.now() + timedelta(days=5)
        allowance = BasicAllowance(
            spend_limit=spend_limit,
            expiration=expiration,
        )

        hash = await client.feegrant.grant_allowance(grantee_address=grantee_key_manager.address, allowance=allowance)
        assert hash
        assert isinstance(hash, str)
        await client.basic.wait_for_tx(hash)

        allowances = await client.feegrant.get_allowances(grantee_address=grantee_key_manager.address)
        assert isinstance(allowances, list)
        assert len(allowances) == 1
        assert all(isinstance(allowance, Grant) for allowance in allowances)


@pytest.mark.requires_config
@pytest.mark.tx
@pytest.mark.slow
@pytest.mark.funds
async def test_get_allowances_by_granter():
    config = get_account_configuration()
    key_manager = KeyManager(private_key=config.private_key)

    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        await client.async_init()

        # Create a new account for the granter, this account will grant the allowance
        granter_key_manager = KeyManager()

        # Create a new account for the grantee, this account will receive the allowance
        grantee_key_manager = KeyManager()

        # No allowances by granter
        allowances = await client.feegrant.get_allowances_by_granter(granter_address=granter_key_manager.address)
        assert isinstance(allowances, list)
        assert len(allowances) == 0

        # Fund both accounts with a transaction with the base account
        # Granter
        hash = await client.account.transfer(
            from_address=key_manager.address,
            to_address=granter_key_manager.address,
            amounts=[Coin(denom="BNB", amount="1500000000000000")],
        )
        assert hash
        await client.basic.wait_for_tx(hash)

        # Grantee
        hash = await client.account.transfer(
            from_address=key_manager.address,
            to_address=grantee_key_manager.address,
            amounts=[Coin(denom="BNB", amount="1500000000000000")],
        )
        assert hash
        assert isinstance(hash, str)
        await client.basic.wait_for_tx(hash)

        # Granter grants allowance to grantee
        await client.set_default_account(granter_key_manager.account)

        spend_limit = [Coin(denom="BNB", amount=str(ALLOWANCE_LIMIT))]
        expiration = datetime.now() + timedelta(days=5)
        allowance = BasicAllowance(
            spend_limit=spend_limit,
            expiration=expiration,
        )

        hash = await client.feegrant.grant_allowance(grantee_address=grantee_key_manager.address, allowance=allowance)
        assert hash
        assert isinstance(hash, str)
        await client.basic.wait_for_tx(hash)

        allowances = await client.feegrant.get_allowances(grantee_address=grantee_key_manager.address)
        assert isinstance(allowances, list)
        assert len(allowances) == 1
        assert all(isinstance(allowance, Grant) for allowance in allowances)

        allowances = await client.feegrant.get_allowances_by_granter(granter_address=granter_key_manager.address)
        assert isinstance(allowances, list)
        assert len(allowances) == 1
        assert all(isinstance(allowance, Grant) for allowance in allowances)


@pytest.mark.requires_config
@pytest.mark.tx
@pytest.mark.slow
@pytest.mark.funds
async def test_revoke_allowance():
    config = get_account_configuration()
    key_manager = KeyManager(private_key=config.private_key)

    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        await client.async_init()

        # Create a new account for the granter, this account will grant the allowance
        granter_key_manager = KeyManager()

        # Create a new account for the grantee, this account will receive the allowance
        grantee_key_manager = KeyManager()

        # Fund both accounts with a transaction with the base account
        # Granter
        hash = await client.account.transfer(
            from_address=key_manager.address,
            to_address=granter_key_manager.address,
            amounts=[Coin(denom="BNB", amount="1500000000000000")],
        )
        assert hash
        await client.basic.wait_for_tx(hash)

        # Grantee
        hash = await client.account.transfer(
            from_address=key_manager.address,
            to_address=grantee_key_manager.address,
            amounts=[Coin(denom="BNB", amount="1500000000000000")],
        )
        assert hash
        assert isinstance(hash, str)
        await client.basic.wait_for_tx(hash)

        # Granter grants allowance to grantee
        await client.set_default_account(granter_key_manager.account)

        spend_limit = [Coin(denom="BNB", amount=str(ALLOWANCE_LIMIT))]
        expiration = datetime.now() + timedelta(days=5)
        allowance = BasicAllowance(
            spend_limit=spend_limit,
            expiration=expiration,
        )

        hash = await client.feegrant.grant_allowance(grantee_address=grantee_key_manager.address, allowance=allowance)
        assert hash
        assert isinstance(hash, str)
        await client.basic.wait_for_tx(hash)

        allowances = await client.feegrant.get_allowances(grantee_address=grantee_key_manager.address)
        assert isinstance(allowances, list)
        assert len(allowances) == 1
        assert all(isinstance(allowance, Grant) for allowance in allowances)

        # The granter revokes the allowance
        await client.set_default_account(granter_key_manager.account)

        hash = await client.feegrant.revoke_allowance(
            granter_address=granter_key_manager.address,
            grantee_address=grantee_key_manager.address,
        )
        assert hash
        assert isinstance(hash, str)
        await client.basic.wait_for_tx(hash)

        # Query the allowance from the granter to the grantee, must raise exception
        with pytest.raises(Exception):
            await client.feegrant.get_basic_allowance(
                granter_address=granter_key_manager.address,
                grantee_address=grantee_key_manager.address,
            )
