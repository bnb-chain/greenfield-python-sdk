import pytest

from greenfield_python_sdk.blockchain_client import CustomChannel
from greenfield_python_sdk.protos.cosmos.base.query.v1beta1 import PageRequest
from greenfield_python_sdk.protos.cosmos.base.v1beta1 import Coin
from greenfield_python_sdk.protos.greenfield.sp import Description


@pytest.fixture
def mock_description(mocker):
    return mocker.MagicMock(spec=Description)


@pytest.fixture
def mock_coin(mocker):
    return mocker.MagicMock(spec=Coin)


@pytest.fixture
def mock_page_request(mocker):
    return mocker.MagicMock(spec=PageRequest)


@pytest.fixture
def mock_channel(mocker):
    return CustomChannel(host="localhost", port=9090)
