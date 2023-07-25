from greenfield_python_sdk.models.eip712_messages.sp.sp_url import CREATE_STORAGE_PROVIDER
from greenfield_python_sdk.protos.greenfield.sp import MsgCreateStorageProvider

TYPES = {
    "Msg1": [
        {"name": "type", "type": "string"},
        {"name": "messages", "type": "TypeAny[]"},
        {"name": "initial_deposit", "type": "TypeMsg1InitialDeposit[]"},
        {"name": "proposer", "type": "string"},
        {"name": "metadata", "type": "string"},
        {"name": "title", "type": "string"},
        {"name": "summary", "type": "string"},
    ],
    "TypeAny": [{"name": "type", "type": "string"}, {"name": "value", "type": "bytes"}],
    "TypeMsg1InitialDeposit": [
        {"name": "denom", "type": "string"},
        {"name": "amount", "type": "string"},
    ],
}

URL_TO_PROTOS_TYPE_MAP = {CREATE_STORAGE_PROVIDER: MsgCreateStorageProvider}
