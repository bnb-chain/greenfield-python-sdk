from unittest.mock import MagicMock

import pytest

from greenfield_python_sdk.blockchain.permission import Permission
from greenfield_python_sdk.protos.greenfield.permission import QueryParamsRequest, QueryStub

pytestmark = [pytest.mark.unit, pytest.mark.asyncio]


@pytest.fixture
def mock_permission(mock_channel):
    permission = Permission(mock_channel)
    permission.query_stub = MagicMock(spec=QueryStub)
    return permission


async def test_permission_get_params(mock_permission):
    await mock_permission.get_params()
    mock_permission.query_stub.params.assert_called_once_with(QueryParamsRequest())
