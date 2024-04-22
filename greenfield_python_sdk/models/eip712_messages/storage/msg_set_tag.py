TYPE_URL = "/greenfield.storage.MsgSetTag"
TYPES = {
    "Msg1": [
        {"name": "type", "type": "string"},
        {"name": "operator", "type": "string"},
        {"name": "resource", "type": "string"},
        {"name": "tags", "type": "TypeMsg1Tags"},
    ],
    "TypeMsg1Tags": [
        {"name": "tags", "type": "TypeMsg1TagsTags[]"},
    ],
    "TypeMsg1TagsTags": [
        {"name": "key", "type": "string"},
        {"name": "value", "type": "string"},
    ],
}
