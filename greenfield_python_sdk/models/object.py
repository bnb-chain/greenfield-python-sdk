from typing import List, Optional

from pydantic import BaseModel

from greenfield_python_sdk.protos.greenfield.storage import ObjectInfo, ResourceTags, ResourceTagsTag, VisibilityType


class CreateObjectOptions(BaseModel):
    visibility: Optional[VisibilityType] = None
    secondary_sp_addresses: Optional[List[str]] = None
    content_type: Optional[str] = ""  # TODO: add enum
    is_replica_type: Optional[bool] = None
    is_async_mode: Optional[bool] = None
    is_serial_compute_mode: Optional[str] = "true"
    tags: Optional[ResourceTags] = None


class PutObjectOptions(BaseModel):
    content_type: Optional[str] = ""  # TODO: add enum
    txn_hash: Optional[str] = ""


class ListObjectsOptions(BaseModel):
    # ShowRemovedObject determines whether to include objects that have been marked as removed in the list.
    # If set to false, these objects will be skipped.
    show_removed_object: Optional[bool] = None

    # StartAfter defines the starting object name for the listing of objects.
    # The listing will start from the next object after the one named in this attribute.
    start_after: Optional[str] = ""

    # ContinuationToken is the token returned from a previous list objects request to indicate where
    # in the list of objects to resume the listing. This is used for pagination.
    continuation_token: Optional[str] = ""

    # Delimiter is a character that is used to group keys.
    # All keys that contain the same str between the prefix and the first occurrence of the delimiter
    # are grouped under a single result element in common prefixes.
    # It is used for grouping keys, currently only '/' is supported.
    delimiter: Optional[str] = "/"

    # Prefix limits the response to keys that begin with the specified prefix.
    # You can use prefixes to separate a bucket into different sets of keys in a way similar to how a file
    # system uses folders.
    prefix: Optional[str] = ""

    # MaxKeys defines the maximum number of keys returned to the response body.
    # If not specified, the default value is 50.
    # The maximum limit for returning objects is 1000
    max_keys: Optional[int] = 0


class GetObjectOption(BaseModel):
    range: Optional[str] = None


class ObjectStat(BaseModel):
    object_name: str
    content_type: str
    size: int


class ObjectInfoResult(BaseModel):
    object_name: str
    id: str
    payload_size: int
    visibility: str
    content_type: str
    checksums: List[str]
    create_at: int


class ListObjectsResult(BaseModel):
    objects: List[ObjectInfoResult]
    key_count: int
    max_keys: int
    is_truncated: bool
    next_continuation_token: str
    name: str
    prefix: str
    delimiter: str
    continuation_token: str


class ObjectMeta(BaseModel):
    object_info: ObjectInfo
    locked_balance: str
    removed: bool
    update_at: int
    delete_at: int
    delete_reason: str
    operator: str
    create_tx_hash: str
    update_tx_hash: str
    seal_tx_hash: str


class ListObjectPoliciesOptions(BaseModel):
    limit: Optional[int] = 50
    start_after: Optional[str] = ""
    endpoint: Optional[str] = ""
    sp_address: Optional[str] = ""


class ObjectPolicies(BaseModel):
    principal_type: int
    principal_value: str
    resource_type: int
    resource_id: str
    create_timestamp: int
    update_timestamp: int
    expiration_time: int
