import asyncio
import json
import time
from typing import List, Tuple

import aiohttp

from greenfield_python_sdk.__version__ import __version__
from greenfield_python_sdk.blockchain_client import BlockchainClient
from greenfield_python_sdk.key_manager import KeyManager
from greenfield_python_sdk.models.basic import ResultBlockResults, ResultCommit, ResultStatus
from greenfield_python_sdk.models.eip712_messages.storage.msg_set_tag import TYPE_URL
from greenfield_python_sdk.protos.cosmos.base.tendermint.v1beta1 import (
    GetBlockByHeightRequest,
    GetBlockByHeightResponse,
    GetLatestBlockResponse,
    GetLatestValidatorSetRequest,
    GetNodeInfoResponse,
    GetValidatorSetByHeightRequest,
    Validator,
)
from greenfield_python_sdk.protos.cosmos.tx.v1beta1 import GetTxRequest, SimulateResponse
from greenfield_python_sdk.protos.greenfield.storage import MsgSetTag, ResourceTags
from greenfield_python_sdk.protos.tendermint.services.block_results.v1 import GetBlockResultsRequest


class Basic:
    blockchain_client: BlockchainClient
    key_manager: KeyManager

    def __init__(self, blockchain_client, key_manager):
        self.blockchain_client = blockchain_client
        self.key_manager = key_manager

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
                else "v1.2.0"
            )

    async def get_status(self) -> ResultStatus:
        self.response = await self.make_requests("status", {})
        self.response["node_info"]["default_node_id"] = self.response["node_info"]["id"]
        return ResultStatus(**self.response)

    async def get_commit(self, height: int) -> ResultCommit:
        self.response = await self.make_requests("commit", {"height": f"{height if height else 0}"})
        for i in range(len(self.response["signed_header"]["commit"]["signatures"])):
            if self.response["signed_header"]["commit"]["signatures"][i]["signature"] == None:
                self.response["signed_header"]["commit"]["signatures"][i]["signature"] = ""
        return ResultCommit(**self.response)

    async def get_latest_block_height(self) -> int:
        response = await self.blockchain_client.tendermint.get_latest_block_height()
        return response

    async def get_latest_block(self) -> GetLatestBlockResponse:
        response = await self.blockchain_client.tendermint.get_latest_block()
        return response

    async def get_syncing(self) -> bool:
        response = await self.blockchain_client.tendermint.get_syncing()
        if response.syncing:
            return response.syncing
        else:
            return False

    async def get_block_by_height(self, height: int) -> GetBlockByHeightResponse:
        request = GetBlockByHeightRequest(height=height)
        response = await self.blockchain_client.tendermint.get_block_by_height(request)
        return response

    async def get_block_result_by_height(self, height: int) -> ResultBlockResults:
        self.response = await self.make_requests("block_results", {"height": f"{height if height else 0}"})
        self.response["consensus_param_updates"]["evidence"]["max_age_duration"] = (
            int(self.response["consensus_param_updates"]["evidence"]["max_age_duration"]) / 1000000000
        )
        fields = ["begin_block_events", "end_block_events", "txs_results", "validator_updates"]
        for field in fields:
            self.response[field] = self.response[field] if self.response[field] else []
        return ResultBlockResults(**self.response)

    async def get_validator_set(self, pagination=None) -> Tuple[int, List[Validator]]:
        request = GetLatestValidatorSetRequest(pagination=pagination)

        response = await self.blockchain_client.tendermint.get_validator_set(request)
        return response.block_height, response.validators

    async def get_validators_by_height(self, height: int) -> List[Validator]:
        request = GetValidatorSetByHeightRequest(height=height)

        response = await self.blockchain_client.tendermint.get_validator_set_by_height(request)
        return response.validators

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

    async def make_requests(self, method: str, params):
        headers = {"Content-Type": "application/json"}
        data = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params,
        }
        async with aiohttp.ClientSession() as session:
            self._resp = await session.post(
                self.blockchain_client.channel.base_url, data=json.dumps(data), headers=headers
            )
            return (await self._resp.json())["result"]

    async def set_tag(self, resource_grn: str, tags: ResourceTags):
        msg_set_tag = MsgSetTag(operator=self.key_manager.address, resource=resource_grn, tags=tags)
        tx_hash = await self.blockchain_client.broadcast_message(messages=[msg_set_tag], type_url=[TYPE_URL])
        return tx_hash
