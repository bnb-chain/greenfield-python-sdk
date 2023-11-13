import re
from typing import List

import html_to_json

from greenfield_python_sdk.models.bucket import EndPointOptions
from greenfield_python_sdk.models.group import (
    GroupMembersPaginationOptions,
    GroupMembersResult,
    GroupsMembers,
    GroupsOwnerPaginationOptions,
    GroupsPaginationOptions,
    GroupsResult,
    ListGroupsByGroupIDResponse,
    ListGroupsOptions,
)
from greenfield_python_sdk.models.request import RequestMeta
from greenfield_python_sdk.protos.greenfield.storage import SourceType
from greenfield_python_sdk.storage_provider.request import Client
from greenfield_python_sdk.storage_provider.utils import convert_key, convert_value


class Group:
    def __init__(self, client: Client):
        self.client = client

    async def list_group(self, name: str, prefix: str, opts: ListGroupsOptions) -> List[GroupsResult]:
        maximum_get_group_list_limit = 1000
        maximum_get_group_list_offset = 100000
        default_get_group_list_limit = 50

        if name == "":
            return []

        if prefix == "":
            return []

        if opts.limit < 0:
            return []
        elif opts.limit > maximum_get_group_list_limit:
            opts.limit = maximum_get_group_list_limit
        elif opts.limit == 0:
            opts.limit = default_get_group_list_limit

        if opts.offset < 0 or opts.offset > maximum_get_group_list_offset:
            return []

        if opts.source_type != "":
            source_types = [member.name for member in SourceType]
            if opts.source_type not in source_types:
                opts.source_type = "SOURCE_TYPE_ORIGIN"

        query_parameters = {
            "group-query": "",
            "limit": opts.limit,
            "name": name,
            "offset": opts.offset,
            "prefix": prefix,
            "source-type": opts.source_type,
        }

        base_url = await self.client._get_in_service_sp()
        request_metadata = RequestMeta(
            query_parameters=query_parameters,
            disable_close_body=True,
            base_url=base_url,
        ).model_dump()

        response = await self.client.prepare_request(base_url, request_metadata, request_metadata["query_parameters"])
        list_group_info = html_to_json.convert(await response.text())["gfspgetgrouplistresponse"][0]
        groups = []
        if "groups" in list_group_info:
            list_groups = list_group_info["groups"]
            for _, group_info in enumerate(list_groups):
                converted_data = {
                    convert_key(key): convert_value(key, value) if value[0] else "" for key, value in group_info.items()
                }
                groups.append(converted_data)
            list_group_info.pop("groups")
            list_group_info = {convert_key(key): convert_value(key, value) for key, value in list_group_info.items()}
            list_group_info["groups"] = groups
        else:
            list_group_info = {convert_key(key): convert_value(key, value) for key, value in list_group_info.items()}
            list_group_info["groups"] = []
        return list_group_info["groups"]

    async def list_group_members(self, group_id: int, opts: GroupMembersPaginationOptions) -> GroupMembersResult:
        query_parameters = {
            "group-members": "",
            "group-id": group_id,
            "start-after": opts.start_after,
            "limit": opts.limit,
        }
        request_metadata = RequestMeta(disable_close_body=True, query_parameters=query_parameters).model_dump()
        base_url = await self.client.get_url(opts.endpoint, opts.sp_address)

        response = await self.client.prepare_request(
            base_url,
            request_metadata,
            request_metadata["query_parameters"],
        )
        list_group_members = html_to_json.convert(await response.text())["gfspgetgroupmembersresponse"]
        if "groups" in list_group_members[0]:
            return self.set_group_members(list_group_members[0]["groups"])
        return GroupMembersResult()

    async def list_groups_by_account(self, opts: GroupsPaginationOptions) -> GroupMembersResult:
        query_parameters = {"user-groups": "", "start-after": opts.start_after, "limit": opts.limit}
        account = opts.account
        if account == "":
            account = self.client.key_manager.address

        request_metadata = RequestMeta(
            disable_close_body=True, user_address=account, query_parameters=query_parameters
        ).model_dump()

        base_url = await self.client.get_url(opts.endpoint, opts.sp_address)
        response = await self.client.prepare_request(
            base_url,
            request_metadata,
            request_metadata["query_parameters"],
        )

        list_group_members = html_to_json.convert(await response.text())["gfspgetusergroupsresponse"]
        if "groups" in list_group_members[0]:
            return self.set_group_members(list_group_members[0]["groups"])
        return GroupMembersResult()

    async def list_groups_by_owner(self, opts: GroupsOwnerPaginationOptions) -> GroupMembersResult:
        query_parameters = {"limit": opts.limit, "owned-groups": "", "start-after": opts.start_after}
        owner = opts.owner
        if owner == "":
            owner = self.client.key_manager.address

        request_metadata = RequestMeta(
            disable_close_body=True, user_address=owner, query_parameters=query_parameters
        ).model_dump()
        base_url = await self.client.get_url(opts.endpoint, opts.sp_address)
        response = await self.client.prepare_request(
            base_url,
            request_metadata,
            request_metadata["query_parameters"],
        )

        list_group_members = html_to_json.convert(await response.text())["gfspgetuserownedgroupsresponse"]
        if "groups" in list_group_members[0]:
            return self.set_group_members(list_group_members[0]["groups"])
        return GroupMembersResult()

    async def list_groups_by_group_id(
        self, group_ids: List[int], opts: EndPointOptions
    ) -> List[ListGroupsByGroupIDResponse]:
        maximum_list_groups_size = 1000

        if len(group_ids) == 0 or len(group_ids) > maximum_list_groups_size:
            return []
        query_parameters = {"groups-query": "", "ids": ",".join([str(i) for i in group_ids])}
        base_url = await self.client.get_url(opts.endpoint, opts.sp_address)

        request_metadata = RequestMeta(disable_close_body=True, query_parameters=query_parameters).model_dump()
        response = await self.client.prepare_request(
            base_url,
            request_metadata,
            request_metadata["query_parameters"],
        )
        list_groups = html_to_json.convert(await response.text())["gfsplistgroupsbyidsresponse"][0]["groupentry"]
        current_groups = []

        if "value" in list_groups[0]:
            for group in list_groups:
                converted_data_list = {
                    convert_key(key): convert_value(key, value) if value[0] else "" for key, value in group.items()
                }
                current_groups.append(ListGroupsByGroupIDResponse(**converted_data_list["value"]))
        return current_groups

    def set_group_members(self, list_group_members) -> GroupMembersResult:
        group_members = []

        if "group" in list_group_members[0]:
            for group in list_group_members:
                converted_data_list = {
                    convert_key(key): convert_value(key, value) if value[0] else "" for key, value in group.items()
                }
                group_members.append(GroupsMembers(**converted_data_list))
        return group_members
