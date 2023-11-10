from typing import Optional

from pydantic import BaseModel

from greenfield_python_sdk.protos.greenfield.payment import StreamRecord


class ListUserPaymentAccountsOptions(BaseModel):
    account: Optional[str] = ""
    endpoint: Optional[str] = ""
    sp_address: Optional[str] = ""


class PaymentAccount(BaseModel):
    address: str
    owner: str
    refundable: bool
    update_at: int
    update_time: int


class ListUserPaymentAccountsResult(BaseModel):
    payment_account: Optional[PaymentAccount] = None
    stream_record: Optional[StreamRecord] = None
