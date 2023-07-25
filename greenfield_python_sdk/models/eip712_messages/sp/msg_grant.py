from greenfield_python_sdk.models.eip712_messages.sp.sp_url import GRANT_DEPOSIT
from greenfield_python_sdk.protos.greenfield.sp import DepositAuthorization

TYPES = {
    "Msg1": [
        {"name": "type", "type": "string"},
        {"name": "granter", "type": "string"},
        {"name": "grantee", "type": "string"},
        {"name": "grant", "type": "TypeMsg1Grant"},
    ],
    "TypeAny": [{"name": "type", "type": "string"}, {"name": "value", "type": "bytes"}],
    "TypeMsg1Grant": [{"name": "authorization", "type": "TypeAny"}, {"name": "expiration", "type": "string"}],
}

URL_TO_PROTOS_TYPE_MAP = {GRANT_DEPOSIT: DepositAuthorization}
