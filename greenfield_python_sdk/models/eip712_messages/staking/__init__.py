from greenfield_python_sdk.models.eip712_messages.staking import (
    msg_begin_redelegate,
    msg_cancel_unbonding_delegation,
    msg_create_validator,
    msg_delegate,
    msg_edit_validator,
    msg_undelegate,
)
from greenfield_python_sdk.models.eip712_messages.staking.staking_url import (
    BEGIN_REDELEGATE,
    CANCEL_UNBONDING_DELEGATION,
    CREATE_VALIDATOR,
    DELEGATE,
    EDIT_VALIDATOR,
    UNDELEGATE,
)

TYPES_MAP = {
    BEGIN_REDELEGATE: msg_begin_redelegate.TYPES,
    CANCEL_UNBONDING_DELEGATION: msg_cancel_unbonding_delegation.TYPES,
    CREATE_VALIDATOR: msg_create_validator.TYPES,
    DELEGATE: msg_delegate.TYPES,
    EDIT_VALIDATOR: msg_edit_validator.TYPES,
    UNDELEGATE: msg_undelegate.TYPES,
}

URL_TO_PROTOS_TYPE_MAP = {**msg_create_validator.URL_TO_PROTOS_TYPE_MAP}
