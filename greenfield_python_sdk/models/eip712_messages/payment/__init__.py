from greenfield_python_sdk.models.eip712_messages.payment import (
    msg_create_payment_account,
    msg_deposit,
    msg_disable_refund,
    msg_withdraw,
)

TYPES_MAP = {
    msg_create_payment_account.TYPE_URL: msg_create_payment_account.TYPES,
    msg_deposit.TYPE_URL: msg_deposit.TYPES,
    msg_withdraw.TYPE_URL: msg_withdraw.TYPES,
    msg_disable_refund.TYPE_URL: msg_disable_refund.TYPES,
}
