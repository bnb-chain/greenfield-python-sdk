from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

import betterproto
from pydantic import BaseModel
from pydantic.dataclasses import dataclass

from greenfield_python_sdk.protos.greenfield.permission import PrincipalType


class RequestMeta(BaseModel):
    method: str = "GET"
    data: Optional[Any] = None
    disable_close_body: bool = False
    txn_hash: str = ""
    is_admin_api: bool = False
    bucket_name: str = ""
    object_name: str = ""
    endpoint: str = ""
    relative_path: str = ""
    query_parameters: Dict[str, Any] = {}
    range_info: str = ""
    txn_msg: bytes = None
    content_type: str = ""
    content_length: int = 0
    content_md5_base64: str = ""
    content_sha256: str = ""
    challenge_info: Dict[str, Any] = {}
    user_address: str = ""
    base_url: str = ""
    url: str = ""
    query_str: str = ""


class SendOptions(BaseModel):
    method: str
    body: Optional[Any] = None
    disable_close_body: Optional[bool] = None
    txn_hash: Optional[str] = None
    is_admin_api: Optional[bool] = None


class ResourceType(Enum):
    RESOURCE_TYPE_BUCKET = "b"
    RESOURCE_TYPE_OBJECT = "o"
    RESOURCE_TYPE_GROUP = "g"


@dataclass(eq=False, repr=False)
class Principal(betterproto.Message):
    type: PrincipalType = betterproto.enum_field(1)
    """
    When the type is an account, its value is sdk.AccAddress().String();
	When the type is a group, its value is math.Uint().String()
    """
    value: str = betterproto.string_field(2)


class PutPolicyOption(BaseModel):
    policy_expire_time: datetime = None
