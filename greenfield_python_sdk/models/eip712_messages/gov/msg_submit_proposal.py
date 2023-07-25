TYPE_URL = "/cosmos.gov.v1.MsgSubmitProposal"
TYPES = {
    "Msg1": [
        {"name": "type", "type": "string"},
        {"name": "messages", "type": "TypeAny[]"},
        {"name": "initial_deposit", "type": "TypeMsg1Amount[]"},
        {"name": "proposer", "type": "string"},
        {"name": "metadata", "type": "string"},
        {"name": "title", "type": "string"},
        {"name": "summary", "type": "string"},
    ],
    "TypeAny": [{"name": "type", "type": "string"}, {"name": "value", "type": "bytes"}],
    "TypeMsg1Amount": [{"name": "denom", "type": "string"}, {"name": "amount", "type": "string"}],
}
