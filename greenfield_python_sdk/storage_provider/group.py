from typing import List

from greenfield_python_sdk.models.group import GroupsResult, ListGroupsOptions
from greenfield_python_sdk.models.request import RequestMeta
from greenfield_python_sdk.protos.greenfield.storage import SourceType
from greenfield_python_sdk.storage_provider.request import Client


class Group:
    def __init__(self, client: Client):
        self.client = client

    async def list_group(self, name: str, prefix: str, opts: ListGroupsOptions) -> List[GroupsResult]:
        maximum_get_group_list_limit = 1000
        maximum_get_group_list_offset = 100000
        default_get_group_list_limit = 50

        if name == "":
            return GroupsResult()

        if prefix == "":
            return GroupsResult()

        if opts.limit < 0:
            return GroupsResult()
        elif opts.limit > maximum_get_group_list_limit:
            opts.limit = maximum_get_group_list_limit
        elif opts.limit == 0:
            opts.limit = default_get_group_list_limit

        if opts.offset < 0 or opts.offset > maximum_get_group_list_offset:
            return GroupsResult()

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
        groups = (await response.json())["groups"]
        return groups
