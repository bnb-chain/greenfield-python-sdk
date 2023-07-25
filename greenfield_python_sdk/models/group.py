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
