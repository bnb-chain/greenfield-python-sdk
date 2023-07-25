from unittest.mock import AsyncMock

import pytest

from greenfield_python_sdk.blockchain.bridge import Bridge
from greenfield_python_sdk.protos.greenfield.bridge import MsgTransferOut, QueryParamsRequest

pytestmark = [pytest.mark.unit, pytest.mark.asyncio]


@pytest.fixture
def mock_bridge(mock_channel):
    bridge = Bridge(mock_channel)
    bridge.query_stub = AsyncMock()
    return bridge


async def test_bridge_get_params(mock_bridge):
    await mock_bridge.get_params()
    mock_bridge.query_stub.params.assert_called_once_with(QueryParamsRequest())
