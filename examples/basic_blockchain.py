import asyncio
import logging

from greenfield_python_sdk.blockchain.utils import wait_for_block_height
from greenfield_python_sdk.blockchain_client import BlockchainClient
from greenfield_python_sdk.config import NetworkConfiguration

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    async with BlockchainClient(NetworkConfiguration()) as client:

        response = await client.tendermint.get_node_info()
        logger.info(f"Node info moniker: {response.default_node_info.moniker}, version: {response.default_node_info.version}")

        response = await client.tendermint.get_latest_block()
        logger.info(f"Latest block header: {response.sdk_block.header}")

        height_before = response.sdk_block.header.height
        logger.info(f"Waiting for block height: {height_before}")

        await wait_for_block_height(client, height_before + 1)

        height = await client.tendermint.get_latest_block_height()
        logger.info(f"Current block height: {height}")

if __name__ == "__main__":
    asyncio.run(main())
