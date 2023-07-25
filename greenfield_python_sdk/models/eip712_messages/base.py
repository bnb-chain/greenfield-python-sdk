BASE_TYPES = {
    "Coin": [{"name": "denom", "type": "string"}, {"name": "amount", "type": "uint256"}],
    "EIP712Domain": [
        {"name": "name", "type": "string"},
        {"name": "version", "type": "string"},
        {"name": "chainId", "type": "uint256"},
        {"name": "verifyingContract", "type": "string"},
        {"name": "salt", "type": "string"},
    ],
    "Fee": [
        {"name": "amount", "type": "Coin[]"},
        {"name": "gas_limit", "type": "uint256"},
        {"name": "payer", "type": "string"},
        {"name": "granter", "type": "string"},
    ],
    "Tx": [
        {"name": "account_number", "type": "uint256"},
        {"name": "chain_id", "type": "uint256"},
        {"name": "fee", "type": "Fee"},
        {"name": "memo", "type": "string"},
        {"name": "sequence", "type": "uint256"},
        {"name": "timeout_height", "type": "uint256"},
        {"name": "msg1", "type": "Msg1"},
    ],
}
