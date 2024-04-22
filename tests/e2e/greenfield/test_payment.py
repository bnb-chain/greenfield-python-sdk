from typing import List

import pytest

from greenfield_python_sdk import (
    GreenfieldClient,
    KeyManager,
    NetworkConfiguration,
    NetworkLocalnet,
    NetworkTestnet,
    get_account_configuration,
)
from greenfield_python_sdk.greenfield.account import Coin
from greenfield_python_sdk.models.payment import ListUserPaymentAccountsOptions, ListUserPaymentAccountsResult

pytestmark = [pytest.mark.asyncio, pytest.mark.e2e]


# Initialize the configuration, key manager
network_configuration = NetworkConfiguration(**NetworkTestnet().model_dump())
localnet_network_configuration = NetworkConfiguration(**NetworkLocalnet().model_dump())


async def test_get_payments_account():
    key_manager = KeyManager()
    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        all_payment_accounts = await client.payment.get_all_payment_accounts()
        assert all_payment_accounts
        assert isinstance(all_payment_accounts, list)

        list_user_payment_accounts = await client.payment.list_user_payment_accounts(
            ListUserPaymentAccountsOptions(account=all_payment_accounts[0].owner)
        )
        payment_account_addresses = [test3.payment_account.address for test3 in list_user_payment_accounts]
        payment_account_owner = ""
        payment_account_owner = next(
            (
                test3.payment_account.owner
                for test3 in list_user_payment_accounts
                if payment_account_owner != test3.payment_account.owner and payment_account_owner == ""
            ),
            payment_account_owner,
        )
        assert list_user_payment_accounts
        assert isinstance(list_user_payment_accounts, List)
        assert all_payment_accounts[0].addr in payment_account_addresses
        assert all_payment_accounts[0].owner == payment_account_owner


@pytest.mark.requires_config
@pytest.mark.tx
@pytest.mark.slow
async def test_deposit():
    # Depends on account
    config = get_account_configuration()
    key_manager = KeyManager(private_key=config.private_key)

    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        await client.async_init()

        tx_hash = await client.account.create_payment_account(address=key_manager.address)
        assert tx_hash
        assert isinstance(tx_hash, str)
        await client.basic.wait_for_tx(tx_hash)

        accounts = await client.account.get_payment_accounts_by_owner(owner=key_manager.address)
        assert isinstance(accounts, list)
        assert isinstance(accounts[0], str)

        tx_hash = await client.payment.deposit(to_address=accounts[0], amount=20)
        assert tx_hash
        assert isinstance(tx_hash, str)
        await client.basic.wait_for_tx(tx_hash)


@pytest.mark.requires_config
@pytest.mark.tx
@pytest.mark.slow
@pytest.mark.localnet
async def test_withdraw():
    # Depends on account
    config = get_account_configuration()
    key_manager = KeyManager(private_key=config.private_key)

    async with GreenfieldClient(
        network_configuration=localnet_network_configuration, key_manager=key_manager
    ) as client:
        await client.async_init()

        new_key_manager = KeyManager()

        hash = await client.account.transfer(
            from_address=key_manager.address,
            to_address=new_key_manager.address,
            amounts=[Coin(denom="BNB", amount="1500000000000000")],
        )
        assert hash
        await client.basic.wait_for_tx(hash)

        await client.set_default_account(new_key_manager.account)

        tx_hash = await client.account.create_payment_account(address=key_manager.address)
        assert tx_hash
        assert isinstance(tx_hash, str)
        await client.basic.wait_for_tx(tx_hash)

        accounts = await client.account.get_payment_accounts_by_owner(owner=key_manager.address)
        assert isinstance(accounts, list)
        assert isinstance(accounts[0], str)

        tx_hash = await client.payment.deposit(to_address=accounts[0], amount=20)
        assert tx_hash
        assert isinstance(tx_hash, str)
        await client.basic.wait_for_tx(tx_hash)

        tx_hash = await client.payment.withdraw(from_address=accounts[0], amount=15)
        assert tx_hash
        assert isinstance(tx_hash, str)
        await client.basic.wait_for_tx(tx_hash)


@pytest.mark.requires_config
@pytest.mark.tx
@pytest.mark.slow
@pytest.mark.localnet
async def test_disable_refund():
    # Depends on account
    config = get_account_configuration()
    key_manager = KeyManager(private_key=config.private_key)

    async with GreenfieldClient(
        network_configuration=localnet_network_configuration, key_manager=key_manager
    ) as client:
        await client.async_init()

        new_key_manager = KeyManager()

        hash = await client.account.transfer(
            from_address=key_manager.address,
            to_address=new_key_manager.address,
            amounts=[Coin(denom="BNB", amount="1500000000000000")],
        )
        assert hash
        await client.basic.wait_for_tx(hash)

        await client.set_default_account(new_key_manager.account)

        tx_hash = await client.account.create_payment_account(address=key_manager.address)
        assert tx_hash
        assert isinstance(tx_hash, str)
        await client.basic.wait_for_tx(tx_hash)

        accounts = await client.account.get_payment_accounts_by_owner(owner=key_manager.address)
        assert isinstance(accounts, list)
        assert isinstance(accounts[0], str)

        tx_hash = await client.payment.deposit(to_address=accounts[0], amount=20)
        assert tx_hash
        assert isinstance(tx_hash, str)
        await client.basic.wait_for_tx(tx_hash)

        tx_hash = await client.payment.disable_refund(address=accounts[0])
        assert tx_hash
        assert isinstance(tx_hash, str)
        await client.basic.wait_for_tx(tx_hash)


@pytest.mark.requires_config
@pytest.mark.tx
@pytest.mark.slow
@pytest.mark.localnet
async def test_get_stream_record():
    # Depends on account
    config = get_account_configuration()
    key_manager = KeyManager(private_key=config.private_key)

    async with GreenfieldClient(
        network_configuration=localnet_network_configuration, key_manager=key_manager
    ) as client:
        await client.async_init()

        new_key_manager = KeyManager()

        hash = await client.account.transfer(
            from_address=key_manager.address,
            to_address=new_key_manager.address,
            amounts=[Coin(denom="BNB", amount="1500000000000000")],
        )
        assert hash
        await client.basic.wait_for_tx(hash)

        await client.set_default_account(new_key_manager.account)

        tx_hash = await client.account.create_payment_account(address=key_manager.address)
        assert tx_hash
        assert isinstance(tx_hash, str)
        await client.basic.wait_for_tx(tx_hash)

        accounts = await client.account.get_payment_accounts_by_owner(owner=key_manager.address)
        assert isinstance(accounts, list)
        assert isinstance(accounts[0], str)

        tx_hash = await client.payment.deposit(to_address=accounts[0], amount=20)
        assert tx_hash
        assert isinstance(tx_hash, str)
        await client.basic.wait_for_tx(tx_hash)

        tx_hash = await client.payment.withdraw(from_address=accounts[0], amount=15)
        assert tx_hash
        assert isinstance(tx_hash, str)
        await client.basic.wait_for_tx(tx_hash)

        records = await client.payment.get_stream_record(accounts[0])
        assert records
