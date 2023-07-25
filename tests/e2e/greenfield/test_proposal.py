import pytest
from betterproto.lib.google.protobuf import Any as AnyMessage

from greenfield_python_sdk import GreenfieldClient, KeyManager, NetworkConfiguration, get_account_configuration
from greenfield_python_sdk.models.proposal import ProposalOptions
from greenfield_python_sdk.protos.cosmos.auth.v1beta1 import QueryModuleAccountByNameRequest
from greenfield_python_sdk.protos.cosmos.base.v1beta1 import Coin
from greenfield_python_sdk.protos.cosmos.gov.v1 import Proposal, VoteOption
from greenfield_python_sdk.protos.greenfield.sp import Description, MsgCreateStorageProvider

pytestmark = [pytest.mark.asyncio, pytest.mark.e2e]
network_configuration = NetworkConfiguration()


@pytest.mark.requires_config
@pytest.mark.tx
@pytest.mark.slow
async def test_submit_proposal():
    config = get_account_configuration()
    key_manager = KeyManager(private_key=config.private_key)
    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        await client.async_init()

        funding_address = KeyManager()
        seal_address = KeyManager()
        approval_address = KeyManager()
        gc_address = KeyManager()

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
            creator=gov_module_address,
            description=Description(moniker="test"),
            sp_address=key_manager.address,
            funding_address=funding_address.address,
            seal_address=seal_address.address,
            approval_address=approval_address.address,
            gc_address=gc_address.address,
            endpoint="https://sp0.greenfield.io",
            deposit=Coin(denom="BNB", amount=str(10000000000000000000000)),
            read_price=str(1 * 10**18),
            free_read_quota=None,
            store_price=str(1 * 10**18),
        )
        msg_create_sp = AnyMessage(type_url="/greenfield.sp.MsgCreateStorageProvider", value=bytes(create_sp))

        proposal_id, tx_hash, _ = await client.proposal.submit_proposal(
            msgs=[msg_create_sp],
            deposit_amount=1000000000000000000,
            title="test",
            summary="test",
            opts=ProposalOptions(metadata="create"),
        )
        assert len(tx_hash) == 64
        assert isinstance(tx_hash, str)
        assert isinstance(proposal_id, int)
        await client.basic.wait_for_tx(hash=tx_hash)

        get_proposal = await client.proposal.get_proposal(proposal_id)
        assert isinstance(get_proposal, Proposal)
        assert get_proposal.id == proposal_id
        assert get_proposal.proposer == key_manager.address

        tx_hash = await client.proposal.vote_proposal(
            proposal_id=proposal_id,
            vote_option=VoteOption.VOTE_OPTION_YES,
            opts=ProposalOptions(),
        )
        assert len(tx_hash) == 64
        assert isinstance(tx_hash, str)
        await client.basic.wait_for_tx(hash=tx_hash)
