import pytest
from betterproto.lib.google.protobuf import Any as AnyMessage

from greenfield_python_sdk import (
    BLSKeyManager,
    GreenfieldClient,
    KeyManager,
    NetworkConfiguration,
    NetworkLocalnet,
    NetworkTestnet,
    get_account_configuration,
)
from greenfield_python_sdk.models.proposal import ProposalOptions
from greenfield_python_sdk.protos.cosmos.auth.v1beta1 import QueryModuleAccountByNameRequest
from greenfield_python_sdk.protos.cosmos.base.v1beta1 import Coin
from greenfield_python_sdk.protos.cosmos.gov.v1 import Proposal, VoteOption
from greenfield_python_sdk.protos.greenfield.sp import Description, MsgCreateStorageProvider

pytestmark = [pytest.mark.asyncio, pytest.mark.e2e]
network_configuration = NetworkConfiguration(**NetworkTestnet().model_dump())
localnet_network_configuration = NetworkConfiguration(**NetworkLocalnet().model_dump())


@pytest.mark.requires_config
@pytest.mark.tx
@pytest.mark.slow
@pytest.mark.localnet
async def test_submit_proposal():
    config = get_account_configuration()
    key_manager = KeyManager(private_key=config.private_key)
    async with GreenfieldClient(
        network_configuration=localnet_network_configuration, key_manager=key_manager
    ) as client:
        await client.async_init()

        funding_address = KeyManager()
        seal_address = KeyManager()
        approval_address = KeyManager()
        gc_address = KeyManager()

        bls_key_manager = BLSKeyManager()

        hash = await client.account.transfer(
            from_address=key_manager.address,
            to_address=funding_address.address,
            amounts=[Coin(denom="BNB", amount="1500000000000000")],
        )
        assert hash
        await client.basic.wait_for_tx(hash)

        gov_module = await client.blockchain_client.cosmos.auth.get_module_account_by_name(
            QueryModuleAccountByNameRequest(name="gov")
        )
        gov_module_address = gov_module.account.value.decode()
        gov_module_address = gov_module_address[4 : len(gov_module_address) - 15]

        create_sp = MsgCreateStorageProvider(
            approval_address=approval_address.address,
            creator=gov_module_address,
            deposit=Coin(denom="BNB", amount=str(100000000000000)),
            description=Description(moniker="test"),
            endpoint="https://sp0.greenfield.io",
            free_read_quota=None,
            funding_address=funding_address.address,
            gc_address=gc_address.address,
            read_price=str(1 * 10**18),
            seal_address=seal_address.address,
            sp_address=key_manager.address,
            store_price=str(1 * 10**18),
            bls_key=bls_key_manager.account.public_key,
            bls_proof=bls_key_manager.account.bls_proof(),
        )
        msg_create_sp = AnyMessage(type_url="/greenfield.sp.MsgCreateStorageProvider", value=bytes(create_sp))

        proposal_id, tx_hash = await client.proposal.submit_proposal(
            msgs=[msg_create_sp],
            deposit_amount=100000000000000,
            title="test",
            summary="test",
            opts=ProposalOptions(metadata="create"),
        )
        assert isinstance(tx_hash, str)
        assert isinstance(proposal_id, int)
        await client.basic.wait_for_tx(hash=tx_hash)

        get_proposal = await client.proposal.get_proposal(proposal_id)
        assert isinstance(get_proposal, Proposal)
        assert get_proposal.id == proposal_id
        assert get_proposal.proposer == key_manager.address
