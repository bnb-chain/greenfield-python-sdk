from eth_utils import to_checksum_address

from greenfield_python_sdk.blockchain_client import BlockchainClient
from greenfield_python_sdk.greenfield.account import Coin
from greenfield_python_sdk.protos.cosmos.distribution.v1beta1 import (
    MsgFundCommunityPool,
    MsgSetWithdrawAddress,
    MsgWithdrawDelegatorReward,
    MsgWithdrawValidatorCommission,
)
from greenfield_python_sdk.storage_client import StorageClient


class Distribution:
    blockchain_client: BlockchainClient
    storage_client: StorageClient

    def __init__(self, blockchain_client, storage_client):
        self.blockchain_client = blockchain_client
        self.storage_client = storage_client

    async def set_withdraw_address(self, withdraw_address: str) -> str:
        delegator_address = to_checksum_address(self.storage_client.key_manager.address)
        withdraw_address = to_checksum_address(withdraw_address)

        message = MsgSetWithdrawAddress(delegator_address=delegator_address, withdraw_address=withdraw_address)

        response = await self.blockchain_client.broadcast_message(
            message=message, type_url="/cosmos.distribution.v1beta1.MsgSetWithdrawAddress"
        )
        return response

    async def withdraw_validator_commission(self, validator_address: str) -> str:
        validator_address = to_checksum_address(validator_address)

        message = MsgWithdrawValidatorCommission(validator_address=validator_address)

        response = await self.blockchain_client.broadcast_message(
            message=message, type_url="/cosmos.distribution.v1beta1.MsgWithdrawValidatorCommission"
        )
        return response

    async def withdraw_delegator_reward(self, validator_address: str) -> str:
        delegator_address = to_checksum_address(self.storage_client.key_manager.address)

        validator_address = to_checksum_address(validator_address)

        message = MsgWithdrawDelegatorReward(delegator_address=delegator_address, validator_address=validator_address)

        response = await self.blockchain_client.broadcast_message(
            message=message, type_url="/cosmos.distribution.v1beta1.MsgWithdrawDelegatorReward"
        )
        return response

    async def fund_community_pool(self, amount: int) -> str:
        amount = [Coin(denom="BNB", amount=str(amount))]
        depositor = to_checksum_address(self.storage_client.key_manager.address)

        message = MsgFundCommunityPool(depositor=depositor, amount=amount)

        response = await self.blockchain_client.broadcast_message(
            message=message, type_url="/cosmos.distribution.v1beta1.MsgFundCommunityPool"
        )
        return response
