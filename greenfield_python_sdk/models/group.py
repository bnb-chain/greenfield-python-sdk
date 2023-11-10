from datetime import datetime
from typing import List

from pydantic import BaseModel

from greenfield_python_sdk.protos.greenfield.storage import GroupInfo


class CreateGroupOptions(BaseModel):
    init_group_members: List[str] = None
    extra: str = ""


class ListGroupsOptions(BaseModel):
    source_type: str = ""
    limit: int = 0
    offset: int = 0


class GroupsResult(BaseModel):
    group: GroupInfo = None
    operator: str = ""
    create_at: int = 0
    create_time: int = 0
    update_at: int = 0
    update_time: int = 0
    removed: bool = False


class UpdateGroupMemberOption(BaseModel):
    expiration_time: List[datetime] = None


class RenewGroupMemberOption(BaseModel):
    expiration_time: List[datetime] = None


class GroupMembersPaginationOptions(BaseModel):
    limit: int = 0
    start_after: str = ""
    endpoint: str = ""
    sp_address: str = ""


class GroupsPaginationOptions(BaseModel):
    limit: int = 0
    start_after: str = ""
    account: str = ""
    endpoint: str = ""
    sp_address: str = ""


class GroupsOwnerPaginationOptions(BaseModel):
    limit: int = 0
    start_after: str = ""
    owner: str = ""
    endpoint: str = ""
    sp_address: str = ""


class GroupsMembers(BaseModel):
    group: GroupInfo = None
    account_id: str = ""
    operator: str = ""
    create_at: int = 0
    create_time: int = 0
    update_at: int = 0
    update_time: int = 0
    removed: bool = False
    expiration_time: int = 0


class GroupMembersResult(BaseModel):
    groups: List[GroupsMembers] = None


class ListGroupsByGroupIDResponse(BaseModel):
    group: GroupInfo = None
    operator: str = ""
    create_at: int = 0
    create_time: int = 0
    update_at: int = 0
    update_time: int = 0
    number_of_members: int = 0
    removed: bool = False
