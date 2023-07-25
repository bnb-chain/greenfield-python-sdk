from unittest.mock import AsyncMock

import pytest

from greenfield_python_sdk.blockchain.challenge import Challenge
from greenfield_python_sdk.protos.greenfield.challenge import (
    MsgAttest,
    MsgSubmit,
    QueryLatestAttestedChallengesRequest,
    VoteResult,
)

pytestmark = [pytest.mark.unit, pytest.mark.asyncio]


@pytest.fixture
def mock_challenge(mock_channel):
    challenge = Challenge(mock_channel)
    challenge.query_stub = AsyncMock()
    return challenge


async def test_challenge_get_latest_attested_challenges(mock_challenge):
    await mock_challenge.get_latest_attested_challenges()
    mock_challenge.query_stub.latest_attested_challenges.assert_called_once_with(QueryLatestAttestedChallengesRequest())
