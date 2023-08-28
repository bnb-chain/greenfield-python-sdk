import pytest

from greenfield_python_sdk import (
    GreenfieldClient,
    KeyManager,
    NetworkConfiguration,
    NetworkTestnet,
    get_account_configuration,
)
from greenfield_python_sdk.greenfield.account import BaseAccount, Coin, PaymentAccount
from greenfield_python_sdk.protos.cosmos.base.query.v1beta1 import PageRequest as Pagination
from greenfield_python_sdk.protos.cosmos.crypto.secp256k1 import PubKey

pytestmark = [pytest.mark.asyncio, pytest.mark.e2e]


# Initialize the configuration, key manager
network_configuration = NetworkConfiguration(**NetworkTestnet().model_dump())
key_manager = KeyManager()


async def test_get_module_accounts():
    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        accounts = await client.account.get_module_accounts()
        assert accounts


async def test_get_module_account_by_name():
    # Depends on get_module_accounts
    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        accounts = await client.account.get_module_accounts()
        assert accounts

        account = await client.account.get_module_account_by_name(name=accounts[0].name)
        assert account
        assert account.name == accounts[0].name
        assert account.permissions == accounts[0].permissions


async def test_get_account_balance():
    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        balance = await client.account.get_account_balance(key_manager.address)
        assert isinstance(balance, int)


@pytest.mark.requires_config
async def test_get_account():
    config = get_account_configuration()
    key_manager = KeyManager(private_key=config.private_key)
    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        account = await client.account.get_account(key_manager.address)
        assert account
        assert isinstance(account, BaseAccount)
        assert isinstance(account.pub_key, PubKey)
        assert isinstance(account.account_number, int)
        assert isinstance(account.sequence, int)


async def test_get_all_payment_accounts():
    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        accounts, _ = await client.account.get_all_payment_accounts()
        assert accounts
        assert isinstance(accounts[0], PaymentAccount)


async def test_get_all_payment_accounts_pagination():
    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        # Test pagination limit
        accounts_0, pagination_response_0 = await client.account.get_all_payment_accounts(
            pagination=Pagination(limit=3)
        )
        assert accounts_0
        assert isinstance(accounts_0[0], PaymentAccount)
        assert pagination_response_0.next_key

        # Test pagination limit + next_key
        accounts_1, pagination_response_1 = await client.account.get_all_payment_accounts(
            pagination=Pagination(limit=3, key=pagination_response_0.next_key)
        )

        assert accounts_1
        assert isinstance(accounts_1[0], PaymentAccount)
        assert pagination_response_1.next_key

        assert accounts_0[0].addr != accounts_1[0].addr
        assert pagination_response_0.next_key != pagination_response_1.next_key


async def test_get_payment_account():
    # Depends on get_all_payment_accounts
    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        accounts, _ = await client.account.get_all_payment_accounts(pagination=Pagination(limit=1))
        assert accounts
        assert isinstance(accounts[0], PaymentAccount)

        account = await client.account.get_payment_account(accounts[0].addr)
        assert account
        assert isinstance(account, PaymentAccount)
        assert account.addr == accounts[0].addr


async def test_get_payment_accounts_by_owner():
    # Depends on get_all_payment_accounts
    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        accounts_0, _ = await client.account.get_all_payment_accounts(pagination=Pagination(limit=1))
        assert accounts_0
        assert isinstance(accounts_0[0], PaymentAccount)

        accounts_1 = await client.account.get_payment_accounts_by_owner(accounts_0[0].owner)
        assert isinstance(accounts_1, list)
        assert isinstance(accounts_1[0], str)


@pytest.mark.requires_config
@pytest.mark.tx
@pytest.mark.slow
async def test_transfer():
    config = get_account_configuration()
    key_manager = KeyManager(private_key=config.private_key)

    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        await client.async_init()

        secondary_key_manager = KeyManager()  # Create a new account for the transfer
        tx_hash = await client.account.transfer(
            from_address=key_manager.address,
            to_address=secondary_key_manager.address,
            amounts=[Coin(denom="BNB", amount="1")],
        )
        assert tx_hash
        assert isinstance(tx_hash, str)
        await client.basic.wait_for_tx(tx_hash)


async def test_multi_transfer():
    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        with pytest.raises(NotImplementedError):
            await client.account.multi_transfer([], [])


@pytest.mark.requires_config
@pytest.mark.tx
async def test_create_payment_account():
    config = get_account_configuration()
    key_manager = KeyManager(private_key=config.private_key)

    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        await client.async_init()
        tx_hash = await client.account.create_payment_account(key_manager.address)
        assert tx_hash
        assert isinstance(tx_hash, str)
        await client.basic.wait_for_tx(tx_hash)
