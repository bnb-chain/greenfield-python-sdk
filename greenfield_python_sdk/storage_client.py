import logging

from greenfield_python_sdk import NetworkConfiguration
from greenfield_python_sdk.key_manager import KeyManager
from greenfield_python_sdk.storage_provider.bucket import Bucket
from greenfield_python_sdk.storage_provider.group import Group
from greenfield_python_sdk.storage_provider.object import Object
from greenfield_python_sdk.storage_provider.request import Client

logger = logging.getLogger(__name__)


class StorageClient:
    bucket: Bucket
    client: Client
    group: Group
    object: Object

    def __init__(
        self,
        network_configuration: NetworkConfiguration,
        key_manager: KeyManager,
        sp_endpoints: dict,
    ):
        self.network_url = network_configuration.host
        self.key_manager = key_manager
        self.sp_endpoints: dict = sp_endpoints

    async def __aenter__(self):
        self.client = await Client(self.network_url, self.key_manager, self.sp_endpoints).__aenter__()
        self.bucket = Bucket(self.client)
        self.object = Object(self.client)
        self.group = Group(self.client)
        return self

    async def close(self):
        if self.client:
            await self.client.close()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
