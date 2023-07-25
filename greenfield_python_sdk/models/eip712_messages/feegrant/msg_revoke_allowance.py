from greenfield_python_sdk.protos.cosmos.feegrant.v1beta1 import BasicAllowance, PeriodicAllowance

TYPE_URL = "/cosmos.feegrant.v1beta1.MsgRevokeAllowance"

TYPES = {
    "Msg1": [
        {"name": "type", "type": "string"},
        {"name": "granter", "type": "string"},
        {"name": "grantee", "type": "string"},
    ]
}
