TYPES = {
    "Msg1": [
        {"name": "type", "type": "string"},
        {"name": "operator", "type": "string"},
        {"name": "group_owner", "type": "string"},
        {"name": "group_name", "type": "string"},
        {"name": "members_to_add", "type": "TypeMsg1MembersToAdd[]"},
        {"name": "members_to_delete", "type": "string[]"},
    ],
    "TypeMsg1MembersToAdd": [
        {"name": "expiration_time", "type": "string"},
        {"name": "member", "type": "string"},
    ],
}
