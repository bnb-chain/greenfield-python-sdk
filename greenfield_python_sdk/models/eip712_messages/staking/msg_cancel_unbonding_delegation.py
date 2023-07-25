TYPES = {
    "Msg1": [
        {"name": "type", "type": "string"},
        {"name": "delegator_address", "type": "string"},
        {"name": "validator_address", "type": "string"},
        {"name": "amount", "type": "TypeMsg1Amount"},
        {"name": "creation_height", "type": "int64"},
    ],
    "TypeMsg1Amount": [{"name": "denom", "type": "string"}, {"name": "amount", "type": "string"}],
}
