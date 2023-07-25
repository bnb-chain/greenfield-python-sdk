TYPE_URL = "/cosmos.distribution.v1beta1.MsgFundCommunityPool"

TYPES = {
    "Msg1": [
        {"name": "type", "type": "string"},
        {"name": "depositor", "type": "string"},
        {"name": "amount", "type": "Coin[]"},
    ],
    "Coin": [{"name": "denom", "type": "string"}, {"name": "amount", "type": "uint256"}],
}
