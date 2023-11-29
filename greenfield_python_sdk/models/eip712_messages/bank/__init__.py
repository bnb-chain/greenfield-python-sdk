from greenfield_python_sdk.models.eip712_messages.bank import msg_multi_send, msg_send

TYPES_MAP = {
    msg_send.TYPE_URL: msg_send.TYPES,
    msg_multi_send.TYPE_URL: msg_multi_send.TYPES,
}
