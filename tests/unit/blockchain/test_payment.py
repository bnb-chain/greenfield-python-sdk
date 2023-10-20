from unittest.mock import AsyncMock

import pytest

from greenfield_python_sdk.blockchain.payment import Payment
from greenfield_python_sdk.protos.greenfield.payment import (
    QueryDynamicBalanceRequest,
    QueryGetStreamRecordRequest,
    QueryParamsRequest,
)

pytestmark = [pytest.mark.unit, pytest.mark.asyncio]


@pytest.fixture
def mock_payment(mock_channel):
    payment = Payment(mock_channel)
    payment.query_stub = AsyncMock()
    return payment


async def test_payment_get_params(mock_payment):
    request = QueryParamsRequest()
    await mock_payment.get_params()
    mock_payment.query_stub.params.assert_called_once_with(request)


async def test_payment_get_stream_record(mock_payment):
    request = QueryGetStreamRecordRequest()
    await mock_payment.get_stream_record(request)
    mock_payment.query_stub.stream_record.assert_called_once_with(request)


async def test_payment_get_dynamic_balance(mock_payment):
    request = QueryDynamicBalanceRequest(account="test_account")
    await mock_payment.get_dynamic_balance(request)
    mock_payment.query_stub.dynamic_balance.assert_called_once_with(request)
