from greenfield_python_sdk.blockchain_client import BlockchainClient
from greenfield_python_sdk.key_manager import KeyManager
from greenfield_python_sdk.protos.greenfield.virtualgroup import (
    GlobalVirtualGroupFamily,
    QueryGlobalVirtualGroupFamilyRequest,
)


class VirtualGroup:
    blockchain_client: BlockchainClient
    key_manager: KeyManager

    def __init__(self, blockchain_client, key_manager):
        self.blockchain_client = blockchain_client
        self.key_manager = key_manager

    async def get_virtual_group_family(self, family_id: int) -> GlobalVirtualGroupFamily:
        response = await self.blockchain_client.virtual_group.global_virtual_group_family(
            QueryGlobalVirtualGroupFamilyRequest(family_id=family_id)
        )
        if response.global_virtual_group_family is None:
            raise Exception("Virtual group family not found")

        return response.global_virtual_group_family
