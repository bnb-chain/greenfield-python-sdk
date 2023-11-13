import pytest

from greenfield_python_sdk import GreenfieldClient, KeyManager, NetworkConfiguration, NetworkTestnet
from greenfield_python_sdk.protos.greenfield.virtualgroup import GlobalVirtualGroupFamily

pytestmark = [pytest.mark.asyncio, pytest.mark.e2e]

network_configuration = NetworkConfiguration(**NetworkTestnet().model_dump())

key_manager = KeyManager()


async def test_get_virtual_group_family():
    async with GreenfieldClient(network_configuration=network_configuration, key_manager=key_manager) as client:
        virtual_group_family = await client.virtual_group.get_virtual_group_family(1)
        assert virtual_group_family
        assert isinstance(virtual_group_family, GlobalVirtualGroupFamily)
