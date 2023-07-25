import asyncio
import base64

import aiohttp
from betterproto import Message

from greenfield_python_sdk.__version__ import __version__
from greenfield_python_sdk.protos.cosmos.auth.v1beta1 import BaseAccount, ModuleAccount
from greenfield_python_sdk.protos.cosmos.crypto.secp256k1 import PubKey


async def parse_account(response):
    account = BaseAccount().parse(data=response.account.value)
    pub_key = PubKey().parse(data=account.pub_key.value)
    account.pub_key = pub_key
    return account


async def parse_module_account(response):
    account = ModuleAccount().parse(data=response.value)
    assert account
    return account


async def wait_for_block_height(blockchain_client, height: int) -> int:
    """Waits for the block with the given height to be committed to the blockchain.

    Args:
        height (int): The height of the block to wait for.
    """
    current_height = 0
    while True:
        latest_block = await blockchain_client.tendermint.get_latest_block()
        current_height = latest_block.sdk_block.header.height
        if current_height >= height:
            break
        await asyncio.sleep(0.5)
    return current_height


class Stream:
    def __init__(self, url, path, grpc_request_type, grpc_response_type):
        self.url = url
        self.path = path
        self.grpc_request_type: Message = grpc_request_type
        self.grpc_response_type: Message = grpc_response_type

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        try:
            await self._resp.release()
        except Exception:
            pass

    async def send_message(self, request, end):
        headers = {
            "Content-Type": "application/json",
            "User-Agent": f"greenfield-python-sdk/{__version__}",
        }
        params = {"path": f'"{self.path}"'}
        endpoint = "/abci_query"
        if bytes(request):
            data = "0x" + bytes(request).hex()  # This took me 2h to find out
            params["data"] = data

        async with aiohttp.ClientSession() as session:
            self._resp = await session.get(self.url + endpoint, headers=headers, params=params)
            self.response = await self._resp.json()

    async def recv_message(self):
        if "error" in self.response:
            raise Exception(self.response["error"])
        if "result" in self.response:
            result = self.response["result"]
            try:
                raw_message = base64.b64decode(result["response"]["value"])
                result = self.grpc_response_type.FromString(data=raw_message)
                return result
            except Exception as e:
                raise Exception(result["response"]["log"])
        else:
            return None


class CustomChannel:
    def __init__(self, host: str, port: int):
        self.base_url = f"{host}:{port}"

    def request(
        self,
        path: str,
        cardinality,
        grpc_request_type,
        grpc_response_type,
        *args,
        **kwargs,
    ):
        return Stream(self.base_url, path, grpc_request_type, grpc_response_type)
