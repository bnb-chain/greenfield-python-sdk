from enum import Enum

from greenfield_python_sdk.__version__ import __version__

PACKAGE = "greenfield-python-sdk"

USER_AGENT = "Greenfield " + PACKAGE + "/" + __version__
ETH_ADDRESS_LENGTH = 20

CREATE_OBJECT_ACTION = "CreateObject"
CREATE_BUCKET_ACTION = "CreateBucket"
SIGN_ALGORITHM = "GNFD1-ECDSA"
AUTH_V1 = "authTypeV1"
SUPPORT_HEADERS = [
    "Content-MD5",
    "Content-Type",
    "Range",
    "X-Gnfd-Content-Sha256",
    "X-Gnfd-Date",
    "X-Gnfd-Expiry-Timestamp",
    "X-Gnfd-Object-ID",
    "X-Gnfd-Piece-Index",
    "X-Gnfd-Redundancy-Index",
    "X-Gnfd-Txn-Hash",
    "X-Gnfd-Unsigned-Msg",
    "X-Gnfd-User-Address",
]


class ListInfoKeys(Enum):
    bucketinfo = "bucket_info"
    bucketname = "bucket_name"
    sourcetype = "source_type"
    createat = "create_at"
    paymentaddress = "payment_address"
    globalvirtualgroupfamilyid = "global_virtual_group_family_id"
    chargedreadquota = "charged_read_quota"
    bucketstatus = "bucket_status"
    deleteat = "delete_at"
    deletereason = "delete_reason"
    createtxhash = "create_tx_hash"
    updatetxhash = "update_tx_hash"
    updateat = "update_at"
    updatetime = "update_time"
    primaryspid = "primary_sp_id"
    virtualpaymentaddress = "virtual_payment_address"
    redundancytype = "redundancy_type"
    objectstatus = "object_status"
    contenttype = "content_type"
    localvirtualgroupid = "local_virtual_group_id"
    objectname = "object_name"
    lockedbalance = "locked_balance"
    objectinfo = "object_info"
    payloadsize = "payload_size"
    sealtxhash = "seal_tx_hash"
    keycount = "key_count"
    maxkeys = "max_keys"
    istruncated = "is_truncated"
    nextcontinuationtoken = "next_continuation_token"
    continuationtoken = "continuation_token"
    numberofmembers = "number_of_members"
    groupname = "group_name"
