TYPE_URL = "/cosmos.bank.v1beta1.MsgMultiSend"
TYPES = {
    "Msg1": [
        {"name": "inputs", "type": "TypeMsg1Inputs[]"},
        {"name": "outputs", "type": "TypeMsg1Outputs[]"},
        {"name": "type", "type": "string"},
    ],
    "TypeMsg1Inputs": [{"name": "address", "type": "string"}, {"name": "coins", "type": "TypeMsg1InputsCoins[]"}],
    "TypeMsg1InputsCoins": [{"name": "amount", "type": "string"}, {"name": "denom", "type": "string"}],
    "TypeMsg1Outputs": [{"name": "address", "type": "string"}, {"name": "coins", "type": "TypeMsg1OutputsCoins[]"}],
    "TypeMsg1OutputsCoins": [{"name": "amount", "type": "string"}, {"name": "denom", "type": "string"}],
}
