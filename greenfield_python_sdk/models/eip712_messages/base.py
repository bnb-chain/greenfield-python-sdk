BASE_TYPES = {
    "Coin": [{"name": "amount", "type": "uint256"}, {"name": "denom", "type": "string"}],
    "EIP712Domain": [
        {"name": "chainId", "type": "uint256"},
        {"name": "name", "type": "string"},
        {"name": "salt", "type": "string"},
        {"name": "verifyingContract", "type": "string"},
        {"name": "version", "type": "string"},
    ],
    "Fee": [
        {"name": "amount", "type": "Coin[]"},
        {"name": "gas_limit", "type": "uint256"},
        {"name": "granter", "type": "string"},
        {"name": "payer", "type": "string"},
    ],
}
