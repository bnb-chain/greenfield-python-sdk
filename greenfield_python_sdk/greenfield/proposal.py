import asyncio
from typing import Any, List, Tuple

from greenfield_python_sdk.blockchain_client import BlockchainClient
from greenfield_python_sdk.models.eip712_messages.proposal.proposal_url import PROPOSAL, VOTE
from greenfield_python_sdk.models.proposal import ProposalOptions
from greenfield_python_sdk.protos.cosmos.base.v1beta1 import Coin
from greenfield_python_sdk.protos.cosmos.gov.v1 import (
    MsgSubmitProposal,
    MsgVote,
    Proposal,
    QueryProposalRequest,
    VoteOption,
)
from greenfield_python_sdk.protos.cosmos.tx.v1beta1 import GetTxRequest
from greenfield_python_sdk.storage_client import StorageClient


class Proposal:
    def __init__(self, blockchain_client: BlockchainClient, storage_client: StorageClient):
        self.blockchain_client = blockchain_client
        self.storage_client = storage_client

    async def submit_proposal(
        self, msgs: List[Any], deposit_amount: int, title: str, summary: str, opts: ProposalOptions
    ) -> Tuple[int, str, Exception]:
        msg_submit_proposal = MsgSubmitProposal(
            initial_deposit=[Coin(denom="BNB", amount=str(deposit_amount))],
            proposer=self.storage_client.key_manager.address,
            metadata=opts.metadata,
            title=title,
            summary=summary,
            messages=msgs,
        )

        tx_resp = await self.blockchain_client.broadcast_message(message=msg_submit_proposal, type_url=PROPOSAL)

        await asyncio.sleep(10)
        request = GetTxRequest(hash=tx_resp)
        resp = await self.blockchain_client.cosmos.tx.get_tx(request)

        for logs in resp.tx_response.logs:
            for events in logs.events:
                for attributes in events.attributes:
                    if attributes.key == "proposal_id":
                        proposal_id = int(attributes.value)
                        return proposal_id, tx_resp, None
        return 0, tx_resp, Exception("ProposalID not found")

    async def vote_proposal(self, proposal_id: int, vote_option: VoteOption, opts: ProposalOptions) -> str:
        msg_vote = MsgVote(
            proposal_id=proposal_id,
            voter=self.storage_client.key_manager.address,
            option=vote_option,
            metadata=opts.metadata,
        )
        resp = await self.blockchain_client.broadcast_message(message=msg_vote, type_url=VOTE)
        return resp

    async def get_proposal(self, proposal_id: int) -> Proposal:
        request = QueryProposalRequest(proposal_id=proposal_id)
        resp = await self.blockchain_client.cosmos.gov.get_proposal(request)
        return resp.proposal
