import pytest
from betterproto.lib.google.protobuf import Any as AnyMessage

from greenfield_python_sdk import GreenfieldClient, KeyManager, NetworkConfiguration, get_account_configuration
from greenfield_python_sdk.greenfield.account import Coin
from greenfield_python_sdk.key_manager import AccountED25519
from greenfield_python_sdk.protos.cosmos.staking.v1beta1 import (
    CommissionRates,
    Description,
    MsgBeginRedelegate,
    MsgBeginRedelegateResponse,
    MsgCancelUnbondingDelegation,
    MsgCancelUnbondingDelegationResponse,
    MsgCreateValidator,
    MsgDelegate,
    MsgDelegateResponse,
    MsgEditValidator,
    MsgEditValidatorResponse,
    MsgStub,
    MsgUndelegate,
    MsgUndelegateResponse,
    QueryDelegationRequest,
    QueryDelegationResponse,
    QueryDelegatorDelegationsRequest,
    QueryDelegatorDelegationsResponse,
    QueryDelegatorUnbondingDelegationsRequest,
    QueryDelegatorUnbondingDelegationsResponse,
    QueryDelegatorValidatorRequest,
    QueryDelegatorValidatorResponse,
    QueryDelegatorValidatorsRequest,
    QueryDelegatorValidatorsResponse,
    QueryHistoricalInfoRequest,
    QueryHistoricalInfoResponse,
    QueryParamsRequest,
    QueryParamsResponse,
    QueryPoolRequest,
    QueryPoolResponse,
    QueryRedelegationsRequest,
    QueryRedelegationsResponse,
    QueryStub,
    QueryUnbondingDelegationRequest,
    QueryUnbondingDelegationResponse,
    QueryValidatorDelegationsRequest,
    QueryValidatorDelegationsResponse,
    QueryValidatorRequest,
    QueryValidatorResponse,
    QueryValidatorsRequest,
    QueryValidatorsResponse,
    QueryValidatorUnbondingDelegationsRequest,
    QueryValidatorUnbondingDelegationsResponse,
)
from greenfield_python_sdk.protos.cosmos.tx.v1beta1 import GetTxRequest

pytestmark = [pytest.mark.asyncio, pytest.mark.e2e]


# Initialize the configuration, key manager
network_configuration = NetworkConfiguration()
key_manager = KeyManager()


async def test_list_validators():
    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        response = await client.validator.list_validators()
        assert response
        assert isinstance(response, QueryValidatorsResponse)

        response = await client.validator.list_validators(status="BOND_STATUS_BONDED")
        assert response
        assert isinstance(response, QueryValidatorsResponse)


@pytest.mark.requires_config
@pytest.mark.tx
@pytest.mark.slow
@pytest.mark.localnet
async def test_create_validator():
    config = get_account_configuration()
    key_manager = KeyManager(private_key=config.private_key)

    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        await client.async_init()
        # Send some tokens to the new validator and the rest of accounts

        new_validator_key_manager = KeyManager()
        new_validator_account_ed25519 = AccountED25519()

        hash = await client.account.transfer(
            from_address=key_manager.address,
            to_address=new_validator_key_manager.address,
            amounts=[Coin(denom="BNB", amount="10010000000000000000")],
        )
        assert hash
        await client.basic.wait_for_tx(hash)

        new_relayer_key_manager = KeyManager()
        hash = await client.account.transfer(
            from_address=key_manager.address,
            to_address=new_relayer_key_manager.address,
            amounts=[Coin(denom="BNB", amount="100100000000000000")],
        )
        assert hash
        await client.basic.wait_for_tx(hash)

        new_challenger_key_manager = KeyManager()
        hash = await client.account.transfer(
            from_address=key_manager.address,
            to_address=new_challenger_key_manager.address,
            amounts=[Coin(denom="BNB", amount="100100000000000000")],
        )
        assert hash
        await client.basic.wait_for_tx(hash)

        # Grant gov module account for proposal execution
        await client.set_default_account(new_validator_key_manager.account)

        hash = await client.validator.grant_delegation_for_validator(
            delegation_amount="100000000000000000",
        )
        assert hash
        await client.basic.wait_for_tx(hash)

        # Create a validator
        tx_hash = await client.validator.create_validator(
            description=Description(
                moniker="test_new_validator",
            ),
            commission=CommissionRates(
                rate="0",
                max_rate="1000000000000000000",
                max_change_rate="1000000000000000000",
            ),
            min_self_delegation_amount="1000000000000000000",
            validator_address=new_validator_key_manager.address,
            ed25519_pub_key=new_validator_account_ed25519.public_key,
            delegator_address=new_validator_key_manager.address,
            relayer_address=new_relayer_key_manager.address,
            challenger_address=new_challenger_key_manager.address,
            # gnfd keys add validator_bls --keyring-backend test --algo eth_bls
            bls_key="a5e140ee80a0ff1552a954701f599622adf029916f55b3157a649e16086a0669900f784d03bff79e69eb8eb7ccfd77d8",
            proposal_deposit_amount="1000000000000000000",
            proposal_title="create new validator",
            proposal_summary="create new validator",
            proposal_meta_data="",
        )

        assert tx_hash


@pytest.mark.requires_config
@pytest.mark.tx
@pytest.mark.slow
@pytest.mark.localnet
async def test_edit_validator():
    config = get_account_configuration()
    key_manager = KeyManager(private_key=config.private_key)

    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        await client.async_init()

        response = await client.validator.list_validators()
        assert response
        assert isinstance(response, QueryValidatorsResponse)

        previous_description = response.validators[0].description
        previous_description.details = "test-validator-edited"

        hash = await client.validator.edit_validator(
            description=previous_description,
            rate=response.validators[0].commission.commission_rates.rate,
            min_self_delegation=response.validators[0].min_self_delegation,
            relayer_address=response.validators[0].relayer_address,
            challenger_address=response.validators[0].challenger_address,
            bls_key=response.validators[0].bls_key.hex(),
        )
        assert hash
        assert isinstance(hash, str)
        await client.basic.wait_for_tx(hash)


@pytest.mark.requires_config
@pytest.mark.tx
@pytest.mark.slow
@pytest.mark.localnet
async def test_delegate_validator():
    config = get_account_configuration()
    key_manager = KeyManager(private_key=config.private_key)

    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        await client.async_init()

        response = await client.validator.list_validators()
        assert response
        assert isinstance(response, QueryValidatorsResponse)

        hash = await client.validator.grant_delegation_for_validator(
            delegation_amount="100000000000000000",
        )
        assert hash
        await client.basic.wait_for_tx(hash)

        hash = await client.validator.delegate_validator(
            validator_address=response.validators[1].operator_address,
            amount="100000000000000000",
        )
        assert hash
        assert isinstance(hash, str)
        await client.basic.wait_for_tx(hash)


@pytest.mark.requires_config
@pytest.mark.tx
@pytest.mark.slow
@pytest.mark.localnet
async def test_begin_redelegate():
    config = get_account_configuration()
    key_manager = KeyManager(private_key=config.private_key)

    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        await client.async_init()

        response = await client.validator.list_validators()
        assert response
        assert isinstance(response, QueryValidatorsResponse)

        hash = await client.validator.grant_delegation_for_validator(
            delegation_amount="100000000000000000",
        )
        assert hash
        await client.basic.wait_for_tx(hash)

        hash = await client.validator.begin_redelegate(
            validator_src_address=response.validators[1].operator_address,
            validator_dest_address=response.validators[0].operator_address,
            amount="100000000000000000",
        )
        assert hash
        assert isinstance(hash, str)
        await client.basic.wait_for_tx(hash)


@pytest.mark.requires_config
@pytest.mark.tx
@pytest.mark.slow
@pytest.mark.localnet
async def test_undelegate():
    config = get_account_configuration()
    key_manager = KeyManager(private_key=config.private_key)

    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        await client.async_init()

        response = await client.validator.list_validators()
        assert response
        assert isinstance(response, QueryValidatorsResponse)

        hash = await client.validator.grant_delegation_for_validator(
            delegation_amount="100000000000000000",
        )
        assert hash
        assert isinstance(hash, str)
        await client.basic.wait_for_tx(hash)

        hash = await client.validator.delegate_validator(
            validator_address=response.validators[1].operator_address,
            amount="100000000000000000",
        )
        assert hash
        assert isinstance(hash, str)
        await client.basic.wait_for_tx(hash)

        hash = await client.validator.undelegate(
            validator_address=response.validators[1].operator_address,
            amount="100000000000000000",
        )
        assert hash
        assert isinstance(hash, str)
        await client.basic.wait_for_tx(hash)


@pytest.mark.requires_config
@pytest.mark.tx
@pytest.mark.slow
@pytest.mark.localnet
async def test_cancel_unbonding_delegation():
    config = get_account_configuration()
    key_manager = KeyManager(private_key=config.private_key)

    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        await client.async_init()

        new_validator_key_manager = KeyManager()

        hash = await client.account.transfer(
            from_address=key_manager.address,
            to_address=new_validator_key_manager.address,
            amounts=[Coin(denom="BNB", amount="1001000000000000000")],
        )
        assert hash
        await client.basic.wait_for_tx(hash)

        response = await client.validator.list_validators()
        assert response
        assert isinstance(response, QueryValidatorsResponse)

        await client.set_default_account(new_validator_key_manager.account)

        hash = await client.validator.grant_delegation_for_validator(
            delegation_amount="90000000000000000",
        )
        assert hash
        assert isinstance(hash, str)
        await client.basic.wait_for_tx(hash)

        hash = await client.validator.delegate_validator(
            validator_address=response.validators[0].operator_address,
            amount="80000000000000000",
        )
        assert hash
        assert isinstance(hash, str)
        await client.basic.wait_for_tx(hash)

        hash = await client.validator.undelegate(
            validator_address=response.validators[1].operator_address,
            amount="70000000000000000",
        )
        assert hash
        assert isinstance(hash, str)
        await client.basic.wait_for_tx(hash)

        tx_info = await client.blockchain_client.cosmos.tx.get_tx(request=GetTxRequest(hash=hash))

        hash = await client.validator.cancel_unbonding_delegation(
            validator_address=response.validators[1].operator_address,
            creation_height=tx_info.tx_response.height,
            amount="60000000000000000",
        )
        assert hash
        assert isinstance(hash, str)
        await client.basic.wait_for_tx(hash)


@pytest.mark.requires_config
@pytest.mark.tx
@pytest.mark.slow
@pytest.mark.localnet
async def test_grant_delegation_for_validator():
    config = get_account_configuration()
    key_manager = KeyManager(private_key=config.private_key)

    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        await client.async_init()

        hash = await client.validator.grant_delegation_for_validator(
            delegation_amount="100000000000000000",
        )
        assert hash
        assert isinstance(hash, str)
        await client.basic.wait_for_tx(hash)


@pytest.mark.requires_config
@pytest.mark.tx
@pytest.mark.slow
@pytest.mark.localnet
async def test_unjail_validator():
    config = get_account_configuration()
    key_manager = KeyManager(private_key=config.private_key)

    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        await client.async_init()

        hash = await client.validator.unjail_validator()
        assert hash
        assert isinstance(hash, str)


@pytest.mark.requires_config
@pytest.mark.tx
@pytest.mark.slow
@pytest.mark.localnet
async def test_impeach_validator():
    config = get_account_configuration()
    key_manager = KeyManager(private_key=config.private_key)

    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        await client.async_init()

        response = await client.validator.list_validators()
        assert response
        assert isinstance(response, QueryValidatorsResponse)
        with pytest.raises(Exception) as excinfo:
            hash = await client.validator.impeach_validator(
                validator_address=response.validators[1].operator_address,
            )

        assert (
            "unrecognized msg type: /cosmos.slashing.v1beta1.MsgImpeach: unknown MsgGasParams type: msg gas params are invalid"
            in str(excinfo.value)
        )
