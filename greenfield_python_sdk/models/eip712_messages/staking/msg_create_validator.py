from greenfield_python_sdk.models.eip712_messages.staking.staking_url import (
    CREATE_VALIDATOR,
    PUBKEY,
    STAKE_AUTHORIZATION,
)
from greenfield_python_sdk.protos.cosmos.crypto.ed25519 import PubKey
from greenfield_python_sdk.protos.cosmos.staking.v1beta1 import MsgCreateValidator, StakeAuthorization

TYPES = {
    "Msg1": [
        {"name": "type", "type": "string"},
        {"name": "description", "type": "TypeMsg1Description"},
        {"name": "commission", "type": "TypeMsg1CommissionRates"},
        {"name": "min_self_delegation", "type": "string"},
        {"name": "delegator_address", "type": "string"},
        {"name": "validator_address", "type": "string"},
        {"name": "pubkey", "type": "TypeAny"},
        {"name": "value", "type": "TypeMsg1Amount"},
        {"name": "from", "type": "string"},
        {"name": "relayer_address", "type": "string"},
        {"name": "challenger_address", "type": "string"},
        {"name": "bls_key", "type": "string"},
    ],
    "TypeMsg1Description": [
        {"name": "moniker", "type": "string"},
        {"name": "identity", "type": "string"},
        {"name": "website", "type": "string"},
        {"name": "security_contact", "type": "string"},
        {"name": "details", "type": "string"},
    ],
    "TypeMsg1CommissionRates": [
        {"name": "rate", "type": "string"},
        {"name": "max_rate", "type": "string"},
        {"name": "max_change_rate", "type": "string"},
    ],
    "TypeAny": [{"name": "type", "type": "string"}, {"name": "value", "type": "bytes"}],
    "TypeMsg1Amount": [{"name": "denom", "type": "string"}, {"name": "amount", "type": "string"}],
}

URL_TO_PROTOS_TYPE_MAP = {
    CREATE_VALIDATOR: MsgCreateValidator,
    PUBKEY: PubKey,
    STAKE_AUTHORIZATION: StakeAuthorization,
}
