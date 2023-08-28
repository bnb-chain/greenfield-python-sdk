TYPE_URL = "/cosmos.bank.v1beta1.MsgSend"
TYPES = {
    "Msg1": [
        {"name": "amount", "type": "TypeMsg1Amount[]"},
        {"name": "from_address", "type": "string"},
        {"name": "to_address", "type": "string"},
        {"name": "type", "type": "string"},
    ],
    "TypeMsg1Amount": [{"name": "amount", "type": "string"}, {"name": "denom", "type": "string"}],
}
