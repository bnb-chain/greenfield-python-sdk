from enum import Enum

from greenfield_python_sdk.__version__ import __version__

PACKAGE = "greenfield-python-sdk"

USER_AGENT = "Greenfield " + PACKAGE + "/" + __version__
ETH_ADDRESS_LENGTH = 20

CREATE_OBJECT_ACTION = "CreateObject"
CREATE_BUCKET_ACTION = "CreateBucket"
MIGRATE_BUCKET_ACTION = "MigrateBucket"
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
    accountid = "account_id"
    bufferbalance = "buffer_balance"
    bucketinfo = "bucket_info"
    bucketname = "bucket_name"
    bucketstatus = "bucket_status"
    chargedreadquota = "charged_read_quota"
    contenttype = "content_type"
    continuationtoken = "continuation_token"
    createat = "create_at"
    createtime = "create_time"
    createtxhash = "create_tx_hash"
    crudtimestamp = "crud_timestamp"
    deleteat = "delete_at"
    deletereason = "delete_reason"
    expirationtime = "expiration_time"
    frozennetflowrate = "frozen_netflow_rate"
    globalvirtualgroupfamilyid = "global_virtual_group_family_id"
    groupname = "group_name"
    istruncated = "is_truncated"
    keycount = "key_count"
    localvirtualgroupid = "local_virtual_group_id"
    lockbalance = "lock_balance"
    lockedbalance = "locked_balance"
    maxkeys = "max_keys"
    netflowrate = "netflow_rate"
    nextcontinuationtoken = "next_continuation_token"
    numberofmembers = "number_of_members"
    objectinfo = "object_info"
    objectname = "object_name"
    objectstatus = "object_status"
    outflowcount = "out_flow_count"
    payloadsize = "payload_size"
    paymentaccount = "payment_account"
    paymentaddress = "payment_address"
    primaryspid = "primary_sp_id"
    redundancytype = "redundancy_type"
    sealtxhash = "seal_tx_hash"
    settletimestamp = "settle_timestamp"
    sourcetype = "source_type"
    staticbalance = "static_balance"
    streamrecord = "stream_record"
    updateat = "update_at"
    updatetime = "update_time"
    updatetxhash = "update_tx_hash"
    virtualpaymentaddress = "virtual_payment_address"
