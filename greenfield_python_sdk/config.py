from functools import lru_cache

from pydantic import BaseModel
from pydantic_settings import BaseSettings

GREENFIELD_VERSION = "v0.2.3"


class NetworkTestnet(BaseModel):
    host: str = "https://gnfd-testnet-fullnode-tendermint-us.bnbchain.org"
    port: int = 443
    chain_id: int = 5600


class NetworkConfiguration(BaseSettings):
    host: str
    port: int
    chain_id: int

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class AccountConfiguration(BaseSettings):
    private_key: str  # private key of the account, hex encoded, i.e. 3460f...

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache(maxsize=1)
def get_account_configuration() -> AccountConfiguration:
    return AccountConfiguration()
