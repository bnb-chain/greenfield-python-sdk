from greenfield_python_sdk.models.eip712_messages.proposal import msg_submit_proposal, msg_vote_proposal
from greenfield_python_sdk.models.eip712_messages.proposal.proposal_url import PROPOSAL, VOTE

TYPES_MAP = {
    PROPOSAL: msg_submit_proposal.TYPES,
    VOTE: msg_vote_proposal.TYPES,
}

URL_TO_PROTOS_TYPE_MAP = {**msg_submit_proposal.URL_TO_PROTOS_TYPE_MAP}
