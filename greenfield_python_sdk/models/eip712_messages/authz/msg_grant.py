TYPE_URL = "/cosmos.auth.v1beta1.MsgGrant"
TYPES = {
    "Msg1": [
        {"name": "type", "type": "string"},
        {"name": "grantee", "type": "string"},
        {"name": "granter", "type": "string"},
        {"name": "grant", "type": "TypeMsg1Grant"},
    ],
    "TypeMsg1Grant": [{"name": "authorization", "type": "TypeAny"}, {"name": "expiration", "type": "string"}],
    "TypeAny": [{"name": "type", "type": "string"}, {"name": "value", "type": "bytes"}],
}
