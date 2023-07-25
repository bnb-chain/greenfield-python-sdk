from enum import Enum
from typing import Optional

from pydantic import BaseModel
from pydantic.dataclasses import dataclass

from greenfield_python_sdk.models.transaction import TxOption
from greenfield_python_sdk.protos.greenfield.storage import Approval, BillingInfo, BucketInfo, SecondarySpObjectsSize
from greenfield_python_sdk.protos.greenfield.storage import VisibilityType
from greenfield_python_sdk.protos.greenfield.storage import VisibilityType as Visibility


class MsgCreateBucket(BaseModel):
    creator: str
    """
    creator defines the account address of bucket creator, it is also the bucket owner.
    """

    bucket_name: str
    """bucket_name defines a globally unique name of bucket"""

    visibility: str
    """
    visibility means the bucket is private or public. if private, only bucket owner or
    grantee can read it,
    otherwise every greenfield user can read it.
    """

    payment_address: str = None
    """
    payment_address defines an account address specified by bucket owner to pay the read
    fee. Default: creator
    """

    primary_sp_address: str
    """primary_sp_address defines the address of primary sp."""

    primary_sp_approval: Approval
    """
    primary_sp_approval defines the approval info of the primary SP which indicates that
    primary sp confirm the user's request.
    """

    charged_read_quota: Optional[int] = None
    """
    charged_read_quota defines the read data that users are charged for, measured in
    bytes.
    The available read data for each user is the sum of the free read data provided by
    SP and
    the ChargeReadQuota specified here.
    """


class gRPCUrl(Enum):
    """gRPCUrl is the gRPC url of the storage provider."""

    CREATE_BUCKET = "/bnbchain.greenfield.storage.Msg/CreateBucket"
    UPDATE_BUCKET = "/bnbchain.greenfield.storage.Msg/UpdateBucketInfo"
    DELETE_BUCKET = "/bnbchain.greenfield.storage.MsgDeleteBucket"
    PUT_POLICY = "/bnbchain.greenfield.storage.Msg/PutPolicy"
    DELETE_POLICY = "/bnbchain.greenfield.storage.Msg/DeletePolicy"


class ReadQuota(BaseModel):
    bucket_name: str
    bucket_id: int
    read_quota_size: int
    sp_free_read_quota_size: int
    read_consumed_size: int


class ReadRecord(BaseModel):
    object_name: str
    object_id: int
    read_account_address: str
    read_timestamp_us: str
    read_size: int


class ListBucketReadRecord(BaseModel):
    next_start_timestamp_us: int
    read_records: Optional[ReadRecord] = []


class ListBucketInfo(BaseModel):
    bucket_info: BucketInfo = None
    removed: bool = False
    delete_at: int = 0
    delete_reason: str = ""
    operator: str = ""
    create_tx_hash: str = ""
    update_tx_hash: str = ""
    update_at: int = 0
    update_time: int = 0


class UpdateBucketOptions(BaseModel):
    charged_read_quota: Optional[int] = None
    payment_address: Optional[str] = ""
    visibility: Optional[Visibility] = Visibility.VISIBILITY_TYPE_UNSPECIFIED


class ListReadRecordOptions(BaseModel):
    start_time_stamp: Optional[int] = 0
    max_records: int = 1000


class DeletePolicyOption:
    tx_opts: TxOption = None


class GRN(BaseModel):
    res_type: str
    group_owner: Optional[str]
    """
    name can be a bucket name, a bucket name/object name or a group name
    """
    name: str


class CreateBucketOptions(BaseModel):
    charged_read_quota: Optional[int] = 0
    creator_address: Optional[str] = ""
    payment_address: Optional[str] = ""
    primary_sp_approval: Optional[Approval] = Approval(expired_height=0)
    visibility: Optional[VisibilityType] = VisibilityType.VISIBILITY_TYPE_UNSPECIFIED
