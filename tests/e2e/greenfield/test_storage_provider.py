import pytest

from greenfield_python_sdk import BLSKeyManager, GreenfieldClient, KeyManager, NetworkConfiguration, NetworkTestnet
from greenfield_python_sdk.config import get_account_configuration
from greenfield_python_sdk.models.storage_provider import CreateStorageProviderOptions, GrantDepositOptions
from greenfield_python_sdk.protos.cosmos.base.v1beta1 import Coin
from greenfield_python_sdk.protos.greenfield.sp import (
    Description,
    QueryStorageProvidersRequest,
    SecondarySpStorePrice,
    SpStoragePrice,
    StorageProvider,
)

pytestmark = [pytest.mark.asyncio, pytest.mark.e2e]

# Initialize the configuration, key manager
network_configuration = NetworkConfiguration(**NetworkTestnet().model_dump())


key_manager = KeyManager()
## Add the storage provider private key
key_manager_sp = KeyManager()


async def test_list_storage_providers():
    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        list_providers = await client.storage_provider.list_storage_providers()
        assert list_providers
        assert isinstance(list_providers, list)
        assert isinstance(list_providers[0], dict)


async def test_get_storage_provider_info():
    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        list_providers = await client.storage_provider.list_storage_providers()
        assert list_providers

        storage_provider_info = await client.storage_provider.get_storage_provider_info(sp_id=list_providers[0]["id"])
        assert storage_provider_info
        assert list_providers[0]["operatorAddress"] == storage_provider_info.operator_address
        assert list_providers[0]["fundingAddress"] == storage_provider_info.funding_address
        assert list_providers[0]["sealAddress"] == storage_provider_info.seal_address
        assert list_providers[0]["approvalAddress"] == storage_provider_info.approval_address
        assert list_providers[0]["gcAddress"] == storage_provider_info.gc_address
        assert list_providers[0]["totalDeposit"] == storage_provider_info.total_deposit
        assert list_providers[0]["endpoint"] == storage_provider_info.endpoint
        assert isinstance(storage_provider_info, StorageProvider)


async def test_get_storage_price():
    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        list_providers = await client.storage_provider.list_storage_providers()
        assert list_providers

        storage_price = await client.storage_provider.get_storage_price(list_providers[0]["operatorAddress"])
        assert storage_price
        assert isinstance(storage_price, SpStoragePrice)


async def test_get_secondary_sp_store_price():
    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        secondary_sp_store_price = await client.storage_provider.get_secondary_sp_store_price()
        assert secondary_sp_store_price
        assert isinstance(secondary_sp_store_price, SecondarySpStorePrice)


@pytest.mark.requires_config
@pytest.mark.tx
@pytest.mark.slow
@pytest.mark.localnet
async def test_grant_deposit_for_storage_provider():
    config = get_account_configuration()
    key_manager = KeyManager(private_key=config.private_key)
    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        await client.async_init()
        sps = (await client.blockchain_client.sp.get_storage_providers(QueryStorageProvidersRequest())).sps
        grant_deposit = await client.storage_provider.grant_deposit_for_storage_provider(
            sp_addr=sps[0].operator_address,
            deposit_amount=10000000000000000000,
            opts=GrantDepositOptions(),
        )
        assert grant_deposit
        assert len(grant_deposit) == 64
        assert isinstance(grant_deposit, str)
        await client.basic.wait_for_tx(grant_deposit)


@pytest.mark.requires_config
@pytest.mark.tx
@pytest.mark.slow
@pytest.mark.localnet
async def test_create_storage_provider():
    config = get_account_configuration()
    key_manager = KeyManager(private_key=config.private_key)
    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        await client.async_init()

        bls_key_manager = BLSKeyManager()

        new_funding_key_manager = KeyManager()
        hash = await client.account.transfer(
            from_address=key_manager.address,
            to_address=new_funding_key_manager.address,
            amounts=[Coin(denom="BNB", amount="1000000000000000000")],
        )
        assert hash
        await client.basic.wait_for_tx(hash)

        new_seal_key_manager = KeyManager()
        hash = await client.account.transfer(
            from_address=key_manager.address,
            to_address=new_seal_key_manager.address,
            amounts=[Coin(denom="BNB", amount="10000000000000000")],
        )
        assert hash
        await client.basic.wait_for_tx(hash)

        new_approval_key_manager = KeyManager()
        hash = await client.account.transfer(
            from_address=key_manager.address,
            to_address=new_approval_key_manager.address,
            amounts=[Coin(denom="BNB", amount="10000000000000000")],
        )
        assert hash
        await client.basic.wait_for_tx(hash)

        new_gc_key_manager = KeyManager()
        hash = await client.account.transfer(
            from_address=key_manager.address,
            to_address=new_gc_key_manager.address,
            amounts=[Coin(denom="BNB", amount="10000000000000000")],
        )
        assert hash
        await client.basic.wait_for_tx(hash)

        proposal_id, hash = await client.storage_provider.create_storage_provider(
            funding_addr=new_funding_key_manager.address,
            seal_addr=new_seal_key_manager.address,
            approval_addr=new_approval_key_manager.address,
            gc_addr=new_gc_key_manager.address,
            endpoint="https://sp0.greenfield.io",
            deposit_amount=10000000000000000,
            description=Description(moniker="test"),
            opts=CreateStorageProviderOptions(
                proposal_meta_data="create",
                proposal_title="test",
                proposal_summary="test",
                proposal_deposit_amount=1 * 10**18,
            ),
            bls_key=bls_key_manager.account.public_key,
            bls_proof=bls_key_manager.account.bls_proof(),
        )
        assert isinstance(proposal_id, int)
        assert hash
        assert len(hash) == 64
        assert isinstance(hash, str)
        await client.basic.wait_for_tx(hash)


@pytest.mark.requires_config
@pytest.mark.tx
@pytest.mark.slow
@pytest.mark.localnet
async def test_update_sp_storage_price():
    config = get_account_configuration()
    key_manager = KeyManager(private_key=config.private_key)
    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager_sp) as client:
        await client.async_init()
        hash = await client.storage_provider.update_sp_storage_price(
            sp_addr=key_manager_sp.address,
            read_price=2,
            store_price=2,
            free_read_quota=0,
        )
        assert hash
        assert len(hash) == 64
        assert isinstance(hash, str)
