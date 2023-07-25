from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import betterproto
from pydantic import BaseModel


class GrantDepositOptions(BaseModel):
    expiration: datetime = None


@dataclass(eq=False, repr=False)
class Any(betterproto.Message):
    type: str = betterproto.string_field(1)
    value: bytes = betterproto.bytes_field(2)


class CreateStorageProviderOptions(BaseModel):
    read_price: Optional[int] = None
    free_read_quota: Optional[int] = None
    store_price: Optional[int] = None
    proposal_deposit_amount: Optional[int] = None
    proposal_title: Optional[str] = None
    proposal_summary: Optional[str] = None
    proposal_meta_data: Optional[str] = None
