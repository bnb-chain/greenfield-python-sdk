from pydantic import BaseModel


class ProposalOptions(BaseModel):
    metadata: str = ""
