from greenfield_python_sdk.models.eip712_messages.storage import (
    msg_cancel_create_object,
    msg_create_bucket,
    msg_create_object,
    msg_delete_bucket,
    msg_delete_object,
    msg_delete_policy,
    msg_migrate_bucket,
    msg_mirror_bucket,
    msg_mirror_group,
    msg_mirror_object,
    msg_put_policy,
    msg_update_bucket_info,
    msg_update_object_info,
)
from greenfield_python_sdk.models.eip712_messages.storage.bucket_url import (
    CREATE_BUCKET,
    DELETE_BUCKET,
    MIGRATE_BUCKET,
    UPDATE_BUCKET_INFO,
)
from greenfield_python_sdk.models.eip712_messages.storage.object_url import (
    CANCEL_CREATE_OBJECT,
    CREATE_OBJECT,
    DELETE_OBJECT,
    UPDATE_OBJECT_INFO,
)
from greenfield_python_sdk.models.eip712_messages.storage.policy_url import DELETE_POLICY, PUT_POLICY

TYPES_MAP = {
    CANCEL_CREATE_OBJECT: msg_cancel_create_object.TYPES,
    CREATE_OBJECT: msg_create_object.TYPES,
    DELETE_OBJECT: msg_delete_object.TYPES,
    UPDATE_OBJECT_INFO: msg_update_object_info.TYPES,
    MIGRATE_BUCKET: msg_migrate_bucket.TYPES,
    CREATE_BUCKET: msg_create_bucket.TYPES,
    DELETE_BUCKET: msg_delete_bucket.TYPES,
    UPDATE_BUCKET_INFO: msg_update_bucket_info.TYPES,
    PUT_POLICY: msg_put_policy.TYPES,
    DELETE_POLICY: msg_delete_policy.TYPES,
    msg_mirror_group.TYPE_URL: msg_mirror_group.TYPES,
    msg_mirror_bucket.TYPE_URL: msg_mirror_bucket.TYPES,
    msg_mirror_object.TYPE_URL: msg_mirror_object.TYPES,
}

URL_TO_PROTOS_TYPE_MAP = {**msg_put_policy.URL_TO_PROTOS_TYPE_MAP}
