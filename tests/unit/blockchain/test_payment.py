from unittest.mock import AsyncMock

import pytest

from greenfield_python_sdk.blockchain.payment import Payment
from greenfield_python_sdk.protos.greenfield.payment import (
    MsgCreatePaymentAccount,
    MsgDeposit,
    MsgDisableRefund,
    MsgWithdraw,
    QueryAllAutoSettleRecordRequest,
    QueryAllPaymentAccountCountRequest,
    QueryAllPaymentAccountRequest,
    QueryAllStreamRecordRequest,
    QueryDynamicBalanceRequest,
    QueryGetPaymentAccountCountRequest,
    QueryGetPaymentAccountRequest,
    QueryGetPaymentAccountsByOwnerRequest,
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


async def test_payment_get_stream_record_all(mock_payment):
    request = QueryAllStreamRecordRequest()
    await mock_payment.get_stream_record_all(request)
    mock_payment.query_stub.stream_record_all.assert_called_once_with(request)


async def test_payment_get_payment_account_count(mock_payment):
    request = QueryGetPaymentAccountCountRequest(owner="test_owner")
    await mock_payment.get_payment_account_count(request)
    mock_payment.query_stub.payment_account_count.assert_called_once_with(request)


async def test_payment_get_payment_account_count_all(mock_payment):
    request = QueryAllPaymentAccountCountRequest()
    await mock_payment.get_payment_account_count_all(request)
    mock_payment.query_stub.payment_account_count_all.assert_called_once_with(request)


async def test_payment_get_payment_account(mock_payment):
    request = QueryGetPaymentAccountRequest(addr="test_addr")
    await mock_payment.get_payment_account(request)
    mock_payment.query_stub.payment_account.assert_called_once_with(request)


async def test_payment_get_payment_account_all(mock_payment):
    request = QueryAllPaymentAccountRequest()
    await mock_payment.get_payment_account_all(request)
    mock_payment.query_stub.payment_account_all.assert_called_once_with(request)


async def test_payment_get_dynamic_balance(mock_payment):
    request = QueryDynamicBalanceRequest(account="test_account")
    await mock_payment.get_dynamic_balance(request)
    mock_payment.query_stub.dynamic_balance.assert_called_once_with(request)


async def test_payment_get_payment_accounts_by_owner(mock_payment):
    request = QueryGetPaymentAccountsByOwnerRequest(owner="test_owner")
    await mock_payment.get_get_payment_accounts_by_owner(request)
    mock_payment.query_stub.get_payment_accounts_by_owner.assert_called_once_with(request)


async def test_payment_get_auto_settle_record_all(mock_payment):
    request = QueryAllAutoSettleRecordRequest()
    await mock_payment.get_auto_settle_record_all(request)
    mock_payment.query_stub.auto_settle_record_all.assert_called_once_with(request)
