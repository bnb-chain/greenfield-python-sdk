from greenfield_python_sdk.protos.cosmos.feegrant.v1beta1 import BasicAllowance, PeriodicAllowance

TYPE_URL = "/cosmos.feegrant.v1beta1.MsgGrantAllowance"

TYPES = {
    "Msg1": [
        {"name": "type", "type": "string"},
        {"name": "granter", "type": "string"},
        {"name": "grantee", "type": "string"},
        {"name": "allowance", "type": "TypeAny"},
    ],
    "TypeAny": [{"name": "type", "type": "string"}, {"name": "value", "type": "bytes"}],
}

URL_TO_PROTOS_TYPE_MAP = {
    "/cosmos.feegrant.v1beta1.BasicAllowance": BasicAllowance,
    "/cosmos.feegrant.v1beta1.PeriodicAllowance": PeriodicAllowance,
}
