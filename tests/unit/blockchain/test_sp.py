from unittest.mock import MagicMock

import pytest

from greenfield_python_sdk.blockchain.sp import Sp
from greenfield_python_sdk.protos.greenfield.sp import (
    MsgCreateStorageProvider,
    MsgDeposit,
    MsgEditStorageProvider,
    MsgStub,
    MsgUpdateSpStoragePrice,
    QueryGetSecondarySpStorePriceByTimeRequest,
    QueryGetSpStoragePriceByTimeRequest,
    QueryParamsRequest,
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


async def test_sp_get_sp_storage_price_by_time(mock_sp):
    sp_addr = "test_sp_addr"
    timestamp = 1234567890

    await mock_sp.get_sp_storage_price_by_time(
        QueryGetSpStoragePriceByTimeRequest(sp_addr=sp_addr, timestamp=timestamp)
    )
    mock_sp.query_stub.query_get_sp_storage_price_by_time.assert_called_once_with(
        QueryGetSpStoragePriceByTimeRequest(sp_addr=sp_addr, timestamp=timestamp)
    )


async def test_sp_get_secondary_sp_store_price_by_time(mock_sp):
    timestamp = 1234567890

    await mock_sp.get_secondary_sp_store_price_by_time(QueryGetSecondarySpStorePriceByTimeRequest(timestamp=timestamp))
    mock_sp.query_stub.query_get_secondary_sp_store_price_by_time.assert_called_once_with(
        QueryGetSecondarySpStorePriceByTimeRequest(timestamp=timestamp)
    )


async def test_sp_get_storage_provider(mock_sp):
    sp_address = "test_sp_address"

    await mock_sp.get_storage_provider(QueryStorageProviderRequest(sp_address=sp_address))
    mock_sp.query_stub.storage_provider.assert_called_once_with(QueryStorageProviderRequest(sp_address=sp_address))
