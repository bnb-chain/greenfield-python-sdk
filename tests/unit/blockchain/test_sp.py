from unittest.mock import MagicMock

import pytest

from greenfield_python_sdk.blockchain.sp import Sp
from greenfield_python_sdk.protos.greenfield.sp import (
    QueryStorageProviderRequest,
    QueryStorageProvidersRequest,
    QueryStub,
)

pytestmark = [pytest.mark.unit, pytest.mark.asyncio]


@pytest.fixture
def mock_sp(mock_channel):
    sp = Sp(mock_channel)
    sp.query_stub = MagicMock(spec=QueryStub)
    return sp


async def test_sp_get_storage_providers(mock_sp, mock_page_request):
    await mock_sp.get_storage_providers(QueryStorageProvidersRequest(pagination=mock_page_request))
    mock_sp.query_stub.storage_providers.assert_called_once_with(
        QueryStorageProvidersRequest(pagination=mock_page_request)
    )


async def test_sp_get_storage_provider(mock_sp):
    sp_id = 1

    await mock_sp.get_storage_provider(QueryStorageProviderRequest(id=sp_id))
    mock_sp.query_stub.storage_provider.assert_called_once_with(QueryStorageProviderRequest(id=sp_id))
