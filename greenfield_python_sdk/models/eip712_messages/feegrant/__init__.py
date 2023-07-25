from greenfield_python_sdk.models.eip712_messages.feegrant import msg_grant_allowance, msg_revoke_allowance

TYPES_MAP = {
    msg_grant_allowance.TYPE_URL: msg_grant_allowance.TYPES,
    msg_revoke_allowance.TYPE_URL: msg_revoke_allowance.TYPES,
}

URL_TO_PROTOS_TYPE_MAP = {**msg_grant_allowance.URL_TO_PROTOS_TYPE_MAP}
