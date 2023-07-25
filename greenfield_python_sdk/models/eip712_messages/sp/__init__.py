from greenfield_python_sdk.models.eip712_messages.sp import msg_create_sp, msg_grant, msg_update_sp_storage_price
from greenfield_python_sdk.models.eip712_messages.sp.sp_url import (
    COSMOS_GRANT,
    SUBMIT_PROPOSAL,
    UPDATE_SP_STORAGE_PRICE,
)

TYPES_MAP = {
    COSMOS_GRANT: msg_grant.TYPES,
    SUBMIT_PROPOSAL: msg_create_sp.TYPES,
    UPDATE_SP_STORAGE_PRICE: msg_update_sp_storage_price.TYPES,
}

URL_TO_PROTOS_TYPE_MAP = {**msg_grant.URL_TO_PROTOS_TYPE_MAP, **msg_create_sp.URL_TO_PROTOS_TYPE_MAP}
