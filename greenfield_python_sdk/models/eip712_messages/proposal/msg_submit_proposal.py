from greenfield_python_sdk.protos.cosmos.staking.v1beta1 import MsgCreateValidator
from greenfield_python_sdk.protos.greenfield.sp import MsgCreateStorageProvider

TYPES = {
    "Msg1": [
        {"name": "initial_deposit", "type": "TypeMsg1InitialDeposit[]"},
        {"name": "messages", "type": "TypeAny[]"},
        {"name": "metadata", "type": "string"},
        {"name": "proposer", "type": "string"},
        {"name": "summary", "type": "string"},
        {"name": "title", "type": "string"},
        {"name": "type", "type": "string"},
    ],
    "TypeAny": [{"name": "type", "type": "string"}, {"name": "value", "type": "bytes"}],
    "TypeMsg1InitialDeposit": [
        {"name": "denom", "type": "string"},
        {"name": "amount", "type": "string"},
    ],
}

URL_TO_PROTOS_TYPE_MAP = {
    "/greenfield.sp.MsgCreateStorageProvider": MsgCreateStorageProvider,
    "/cosmos.staking.v1beta1.MsgCreateValidator": MsgCreateValidator,
}
