TYPES = {
    "Msg1": [
        {
            "name": "expiration_time",
            "type": "string",
        },
        {
            "name": "operator",
            "type": "string",
        },
        {
            "name": "principal",
            "type": "TypeMsg1Principal",
        },
        {
            "name": "resource",
            "type": "string",
        },
        {
            "name": "statements",
            "type": "TypeMsg1Statements[]",
        },
        {
            "name": "type",
            "type": "string",
        },
    ],
    "TypeMsg1Principal": [
        {
            "name": "type",
            "type": "string",
        },
        {
            "name": "value",
            "type": "string",
        },
    ],
    "TypeMsg1Statements": [
        {
            "name": "actions",
            "type": "string[]",
        },
        {
            "name": "effect",
            "type": "string",
        },
        {
            "name": "expiration_time",
            "type": "string",
        },
    ],
}

URL_TO_PROTOS_TYPE_MAP = {}
