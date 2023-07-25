from greenfield_python_sdk.models.eip712_messages.distribution import (
    msg_fund_community_pool,
    msg_set_withdraw_address,
    msg_withdraw_delegator_reward,
    msg_withdraw_validator_commission,
)

TYPES_MAP = {
    msg_set_withdraw_address.TYPE_URL: msg_set_withdraw_address.TYPES,
    msg_withdraw_validator_commission.TYPE_URL: msg_withdraw_validator_commission.TYPES,
    msg_withdraw_delegator_reward.TYPE_URL: msg_withdraw_delegator_reward.TYPES,
    msg_fund_community_pool.TYPE_URL: msg_fund_community_pool.TYPES,
}
