TYPES = {
    "Msg1": [
        {"name": "group_name", "type": "string"},
        {"name": "group_owner", "type": "string"},
        {"name": "members", "type": "TypeMsg1Members[]"},
        {"name": "operator", "type": "string"},
        {"name": "type", "type": "string"},
    ],
    "TypeMsg1Members": [
        {"name": "expiration_time", "type": "string"},
        {"name": "member", "type": "string"},
    ],
}
