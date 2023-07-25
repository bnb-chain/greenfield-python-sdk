from greenfield_python_sdk.models.eip712_messages.slashing import msg_impeach, msg_unjail

TYPES_MAP = {
    msg_unjail.TYPE_URL: msg_unjail.TYPES,
    msg_impeach.TYPE_URL: msg_impeach.TYPES,
}
