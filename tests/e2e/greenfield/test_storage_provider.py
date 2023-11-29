import pytest

from greenfield_python_sdk import (
    BLSKeyManager,
    GreenfieldClient,
    KeyManager,
    NetworkConfiguration,
    NetworkLocalnet,
    NetworkTestnet,
)
from greenfield_python_sdk.config import get_account_configuration
from greenfield_python_sdk.models.storage_provider import CreateStorageProviderOptions, GrantDepositOptions
from greenfield_python_sdk.protos.cosmos.base.v1beta1 import Coin
from greenfield_python_sdk.protos.greenfield.sp import (
    Description,
    GlobalSpStorePrice,
    QueryStorageProviderByOperatorAddressRequest,
    QueryStorageProvidersRequest,
    SpStoragePrice,
    Status,
    StorageProvider,
)

pytestmark = [pytest.mark.asyncio, pytest.mark.e2e]

# Initialize the configuration, key manager
network_configuration = NetworkConfiguration(**NetworkTestnet().model_dump())
localnet_network_configuration = NetworkConfiguration(**NetworkLocalnet().model_dump())


key_manager = KeyManager()
## Add the storage provider private key
# key_manager_sp = KeyManager()


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


async def test_get_sp_by_operator_address():
    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        list_providers = await client.storage_provider.list_storage_providers()
        assert list_providers

        storage_provider = await client.blockchain_client.sp.get_sp_by_operator_address(
            QueryStorageProviderByOperatorAddressRequest(operator_address=list_providers[0]["operatorAddress"])
        )
        assert storage_provider
        assert storage_provider.storage_provider.operator_address == list_providers[0]["operatorAddress"]


async def test_get_storage_price():
    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        list_providers = await client.storage_provider.list_storage_providers()
        assert list_providers

        storage_price = await client.storage_provider.get_storage_price(list_providers[0]["operatorAddress"])
        assert storage_price
        assert isinstance(storage_price, SpStoragePrice)


async def test_get_global_sp_store_price():
    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        global_sp_store_price = await client.storage_provider.get_global_sp_store_price()
        assert global_sp_store_price
        assert isinstance(global_sp_store_price, GlobalSpStorePrice)


@pytest.mark.requires_config
@pytest.mark.tx
@pytest.mark.slow
@pytest.mark.localnet
async def test_grant_deposit_for_storage_provider():
    config = get_account_configuration()
    key_manager = KeyManager(private_key=config.private_key)
    async with GreenfieldClient(
        network_configuration=localnet_network_configuration, key_manager=key_manager
    ) as client:
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
    async with GreenfieldClient(
        network_configuration=localnet_network_configuration, key_manager=key_manager
    ) as client:
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

        new_maintenance_key_manager = KeyManager()
        hash = await client.account.transfer(
            from_address=key_manager.address,
            to_address=new_maintenance_key_manager.address,
            amounts=[Coin(denom="BNB", amount="10000000000000000")],
        )
        assert hash
        await client.basic.wait_for_tx(hash)

        proposal_id, hash = await client.storage_provider.create_storage_provider(
            funding_addr=new_funding_key_manager.address,
            seal_addr=new_seal_key_manager.address,
            approval_addr=new_approval_key_manager.address,
            gc_addr=new_gc_key_manager.address,
            maintenance_addr=new_maintenance_key_manager.address,
            endpoint="https://sp0.greenfield.io",
            deposit_amount=10000000000000000000000,
            description=Description(moniker="test"),
            bls_key=bls_key_manager.account.public_key,
            bls_proof=bls_key_manager.account.bls_proof(),
            opts=CreateStorageProviderOptions(
                proposal_meta_data="create",
                proposal_title="test",
                proposal_summary="test",
                proposal_deposit_amount=1 * 10**18,
            ),
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
@pytest.mark.requires_storage_provider
async def test_update_sp_storage_price():
    config = get_account_configuration()
    key_manager = KeyManager(private_key=config.private_key)
    async with GreenfieldClient(
        network_configuration=localnet_network_configuration, key_manager=key_manager
    ) as client:
        await client.async_init()
        hash = await client.storage_provider.update_sp_storage_price(
            sp_addr=key_manager.address,
            read_price=2,
            store_price=2,
            free_read_quota=0,
        )
        assert hash
        assert len(hash) == 64
        assert isinstance(hash, str)


@pytest.mark.requires_config
@pytest.mark.tx
@pytest.mark.slow
@pytest.mark.localnet
@pytest.mark.requires_storage_provider
async def test_update_sp_storage_price():
    config = get_account_configuration()
    key_manager = KeyManager(private_key=config.private_key)
    async with GreenfieldClient(
        network_configuration=localnet_network_configuration, key_manager=key_manager
    ) as client:
        await client.async_init()
        tx_hash = await client.storage_provider.update_sp_status(
            key_manager.address, Status.STATUS_IN_MAINTENANCE, 1000
        )
        assert tx_hash
        assert len(tx_hash) == 64
        assert isinstance(tx_hash, str)
