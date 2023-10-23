from datetime import datetime, timezone
from typing import List, Optional

from greenfield_python_sdk.blockchain_client import BlockchainClient
from greenfield_python_sdk.models.eip712_messages.group.group_url import (
    CREATE_GROUP,
    DELETE_GROUP,
    LEAVE_GROUP,
    UPDATE_GROUP_MEMBER,
)
from greenfield_python_sdk.models.eip712_messages.storage.policy_url import DELETE_POLICY, PUT_POLICY
from greenfield_python_sdk.models.group import CreateGroupOptions, GroupsResult, ListGroupsOptions
from greenfield_python_sdk.models.request import Principal, PutPolicyOption, ResourceType
from greenfield_python_sdk.protos.greenfield.permission import ActionType, Effect, Policy, PrincipalType, Statement
from greenfield_python_sdk.protos.greenfield.resource import ResourceType as UserType
from greenfield_python_sdk.protos.greenfield.storage import (
    GroupInfo,
    MsgCreateGroup,
    MsgDeleteGroup,
    MsgDeletePolicy,
    MsgGroupMember,
    MsgLeaveGroup,
    MsgPutPolicy,
    MsgUpdateGroupMember,
    QueryHeadGroupMemberRequest,
    QueryHeadGroupRequest,
    QueryPolicyForAccountRequest,
    QueryPolicyForGroupRequest,
)
from greenfield_python_sdk.storage_client import StorageClient
from greenfield_python_sdk.storage_provider.utils import check_address


class Group:
    blockchain_client: BlockchainClient
    storage_client: StorageClient

    def __init__(self, blockchain_client, storage_client):
        self.blockchain_client = blockchain_client
        self.storage_client = storage_client

    async def create_group(self, group_name: str, opts: CreateGroupOptions) -> str:
        msg_create_group = MsgCreateGroup(
            creator=self.storage_client.key_manager.address,
            group_name=group_name,
            # members=opts.init_group_members,
            extra=opts.extra,
        )
        tx_hash = await self.blockchain_client.broadcast_message(message=msg_create_group, type_url=CREATE_GROUP)
        return tx_hash

    async def delete_group(self, group_name: str) -> str:
        msg_delete_group = MsgDeleteGroup(
            operator=self.storage_client.key_manager.address,
            group_name=group_name,
        )
        tx_hash = await self.blockchain_client.broadcast_message(message=msg_delete_group, type_url=DELETE_GROUP)
        return tx_hash

    async def update_group_member(
        self,
        group_name: str,
        group_owner: str,
        add_addresses: List[str],
        remove_addresses: List[str],
    ) -> str:
        group_owner = check_address(group_owner)
        if group_name == "":
            raise ValueError("Group name cannot be empty")
        if len(add_addresses) == 0 and len(remove_addresses) == 0:
            raise ValueError("No changes to group members")

        add_members = []

        for address in add_addresses:
            add_members.append(
                MsgGroupMember(
                    member=check_address(address),
                    expiration_time=datetime(2099, 12, 31, 23, 59, 59, tzinfo=timezone.utc),
                )
            )

        msg_update_group_member = MsgUpdateGroupMember(
            operator=self.storage_client.key_manager.address,
            group_owner=group_owner,
            group_name=group_name,
        )

        if len(add_members) > 0:
            msg_update_group_member.members_to_add = add_members

        if len(remove_addresses) > 0:
            msg_update_group_member.members_to_delete = remove_addresses

        tx_hash = await self.blockchain_client.broadcast_message(
            message=msg_update_group_member, type_url=UPDATE_GROUP_MEMBER
        )
        return tx_hash

    async def leave_group(self, group_name: str, group_owner: str) -> str:
        msg_leave_group = MsgLeaveGroup(
            member=self.storage_client.key_manager.address,
            group_owner=check_address(group_owner),
            group_name=group_name,
        )
        tx_hash = await self.blockchain_client.broadcast_message(message=msg_leave_group, type_url=LEAVE_GROUP)
        return tx_hash

    async def get_group_head(self, group_name: str, group_owner: str) -> GroupInfo:
        request = QueryHeadGroupRequest(group_owner=group_owner, group_name=group_name)
        group_head = await self.blockchain_client.storage.get_head_group(request)
        if group_head.group_info == None:
            raise Exception("Group not found")
        return group_head.group_info

    async def get_group_member_head(self, group_name: str, group_owner: str, head_member: str) -> bool:
        request = QueryHeadGroupMemberRequest(member=head_member, group_owner=group_owner, group_name=group_name)
        group_member_head = await self.blockchain_client.storage.get_head_group_member(request)
        return True if group_member_head.group_member != None else False

    async def put_group_policy(
        self, group_name: str, principal_addr: str, statements: List[Statement], opts: Optional[PutPolicyOption] = None
    ) -> str:
        resource = (
            f"grn:{ResourceType.RESOURCE_TYPE_GROUP.value}:{self.storage_client.key_manager.address}:{group_name}"
        )
        principal = Principal(type=PrincipalType.PRINCIPAL_TYPE_GNFD_ACCOUNT, value=principal_addr)
        put_policy_msg = MsgPutPolicy(
            operator=self.storage_client.key_manager.address,
            resource=str(resource),
            principal=principal,
            statements=statements,
        )
        if opts and opts.policy_expire_time:
            put_policy_msg.expiration_time = opts.policy_expire_time

        tx_hash = await self.blockchain_client.broadcast_message(message=put_policy_msg, type_url=PUT_POLICY)
        return tx_hash

    async def delete_group_policy(self, group_name: str, principal_addr: str) -> str:
        principal = Principal(type=PrincipalType.PRINCIPAL_TYPE_GNFD_ACCOUNT, value=check_address(principal_addr))
        resource = (
            f"grn:{ResourceType.RESOURCE_TYPE_GROUP.value}:{self.storage_client.key_manager.address}:{group_name}"
        )

        delete_policy_msg = MsgDeletePolicy(
            operator=self.storage_client.key_manager.address,
            resource=str(resource),
            principal=principal,
        )
        tx_hash = await self.blockchain_client.broadcast_message(message=delete_policy_msg, type_url=DELETE_POLICY)
        return tx_hash

    async def get_bucket_policy_of_group(self, bucket_name: str, group_id: str) -> Policy:
        resource = f"grn:{ResourceType.RESOURCE_TYPE_BUCKET.value}::{bucket_name}"
        request = QueryPolicyForGroupRequest(resource=resource, principal_group_id=group_id)
        policy = await self.blockchain_client.storage.get_policy_for_group(request)
        return self.prepare_policy(policy.policy)

    async def get_object_policy_of_group(self, bucket_name: str, object_name: str, group_id: int) -> Policy:
        resource = f"grn:{ResourceType.RESOURCE_TYPE_OBJECT.value}::{bucket_name}/{object_name}"
        request = QueryPolicyForGroupRequest(resource=resource, principal_group_id=group_id)
        policy = await self.blockchain_client.storage.get_policy_for_group(request)

        return self.prepare_policy(policy.policy)

    async def get_group_policy(self, group_name: str, principal_addr: str) -> Policy:
        check_address(principal_addr)
        resource = (
            f"grn:{ResourceType.RESOURCE_TYPE_GROUP.value}:{self.storage_client.key_manager.address}:{group_name}"
        )
        request = QueryPolicyForAccountRequest(resource=resource, principal_address=principal_addr)
        policy = await self.blockchain_client.storage.get_policy_for_account(request)

        return self.prepare_policy(policy.policy)

    async def list_group(self, name: str, prefix: str, opts: ListGroupsOptions) -> List[GroupsResult]:
        list_group = await self.storage_client.group.list_group(name, prefix, opts)
        return list_group

    def prepare_policy(self, policy: Policy) -> Policy:
        if policy == None:
            raise Exception("Policy not found")

        policy.principal.type = (PrincipalType(policy.principal.type).name)[20:]
        policy.resource_type = (UserType(policy.resource_type).name)[14:]
        policy.statements[0].effect = (Effect(policy.statements[0].effect).name)[7:]
        actions = []
        for i in range(len(policy.statements[0].actions)):
            actions.append(ActionType(policy.statements[0].actions[i]).name)
        policy.statements[0].actions = actions
        return policy
