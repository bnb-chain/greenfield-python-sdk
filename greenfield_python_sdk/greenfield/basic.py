import asyncio
import time
from typing import List, Tuple

import aiohttp

from greenfield_python_sdk.__version__ import __version__
from greenfield_python_sdk.blockchain_client import BlockchainClient
from greenfield_python_sdk.protos.cosmos.base.query.v1beta1 import PageResponse as PaginationResponse
from greenfield_python_sdk.protos.cosmos.base.tendermint.v1beta1 import (
    GetBlockByHeightRequest,
    GetBlockByHeightResponse,
    GetLatestBlockResponse,
    GetLatestValidatorSetRequest,
    GetNodeInfoResponse,
    Validator,
)
from greenfield_python_sdk.protos.cosmos.tx.v1beta1 import GetTxRequest, SimulateResponse


class Basic:
    blockchain_client: BlockchainClient

    def __init__(self, blockchain_client):
        self.blockchain_client = blockchain_client

    async def get_node_info(self) -> GetNodeInfoResponse:
        response = await self.blockchain_client.tendermint.get_node_info()
        return response

    async def get_greenfield_node_version(self) -> str:
        headers = {"Content-Type": "application/json", "User-Agent": f"greenfield-python-sdk/{__version__}"}
        endpoint = "/abci_info"

        async with aiohttp.ClientSession() as session:
            self._resp = await session.get(self.blockchain_client.channel.base_url + endpoint, headers=headers)
            self.response = await self._resp.json()
            return (
                self.response["result"]["response"]["version"]
                if "version" in self.response["result"]["response"]
                else "v1.0.0"
            )

    async def get_status(self):
        raise NotImplementedError

    async def get_commit(self):
        raise NotImplementedError

    async def get_latest_block_height(self) -> int:
        response = await self.blockchain_client.tendermint.get_latest_block_height()
        return response

    async def get_latest_block(self) -> GetLatestBlockResponse:
        response = await self.blockchain_client.tendermint.get_latest_block()
        return response

    async def get_syncing(self):
        response = await self.blockchain_client.tendermint.get_syncing()
        if response.to_pydict():
            return response
        raise NotImplementedError

    async def get_block_by_height(self, height: int) -> GetBlockByHeightResponse:
        request = GetBlockByHeightRequest(height=height)
        response = await self.blockchain_client.tendermint.get_block_by_height(request)
        return response

    async def get_latest_validator_set(self, pagination=None) -> Tuple[List[Validator], PaginationResponse]:
        request = GetLatestValidatorSetRequest(pagination=pagination)

        response = await self.blockchain_client.tendermint.get_latest_validator_set(request)
        return response.validators, response.pagination

    async def get_validator_set(self):
        raise NotImplementedError

    async def get_validators_by_height(self):
        raise NotImplementedError

    async def wait_for_block_height(self, height: int) -> int:
        """Waits for the block with the given height to be committed to the blockchain.

        Args:
            height (int): The height of the block to wait for.
        """
        current_height = 0
        while True:
            latest_block = await self.blockchain_client.tendermint.get_latest_block()
            current_height = latest_block.sdk_block.header.height
            if current_height >= height:
                break
            await asyncio.sleep(0.5)
        return current_height

    async def wait_for_tx(self, hash: str, timeout: int = 60):
        """Waits for the transaction with the given hash to be committed to the blockchain.
        Has a default timeout of 60 seconds.
        """
        initial_time = time.time()
        while True:
            current_time = time.time()
            if current_time - initial_time > timeout:
                raise TimeoutError
            try:
                response = await self.blockchain_client.cosmos.tx.get_tx(GetTxRequest(hash=hash))
                return response
            except Exception:
                await asyncio.sleep(0.5)

    async def wait_for_n_blocks(self, n: int):
        block_height = await self.get_latest_block_height()
        target_height = block_height + n
        response = await self.wait_for_block_height(target_height)
        return response

    async def wait_for_next_block(self):
        block_height = await self.get_latest_block_height()
        target_height = block_height + 1
        response = await self.wait_for_block_height(target_height)
        return response

    async def simulate_tx(self, tx) -> SimulateResponse:
        response = await self.blockchain_client.simulate_tx(tx=tx)
        return response

    async def simulate_raw_tx(self, tx_bytes: bytes):
        response = await self.blockchain_client.simulate_raw_tx(tx_bytes=tx_bytes)
        return response

    async def broadcast_tx(self, tx) -> str:
        response = await self.blockchain_client.broadcast_tx(tx=tx)
        return response

    async def broadcast_raw_tx(self, tx_bytes: bytes) -> str:
        response = await self.blockchain_client.broadcast_raw_tx(tx_bytes=tx_bytes)
        return response

    async def query_vote(self):
        raise NotImplementedError
