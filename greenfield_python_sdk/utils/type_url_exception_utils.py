import base64
import binascii
import json
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional

from betterproto import Casing

from greenfield_python_sdk.__version__ import __version__
from greenfield_python_sdk.models.eip712_messages.group.group_url import (
    CREATE_GROUP,
    RENEW_GROUP_MEMBER,
    UPDATE_GROUP_MEMBER,
)
from greenfield_python_sdk.models.eip712_messages.proposal.proposal_url import VOTE
from greenfield_python_sdk.models.eip712_messages.sp.sp_url import (
    COSMOS_GRANT,
    CREATE_STORAGE_PROVIDER,
    UPDATE_SP_STATUS,
    UPDATE_SP_STORAGE_PRICE,
)
from greenfield_python_sdk.models.eip712_messages.staking.staking_url import (
    CREATE_VALIDATOR,
    EDIT_VALIDATOR,
    STAKE_AUTHORIZATION,
)
from greenfield_python_sdk.models.eip712_messages.storage.bucket_url import CREATE_BUCKET, MIGRATE_BUCKET
from greenfield_python_sdk.models.eip712_messages.storage.object_url import CREATE_OBJECT
from greenfield_python_sdk.models.eip712_messages.storage.policy_url import DELETE_POLICY, PUT_POLICY
from greenfield_python_sdk.models.transaction import BroadcastOption
from greenfield_python_sdk.protos.cosmos.gov.v1 import VoteOption
from greenfield_python_sdk.protos.greenfield.permission import ActionType, Effect, PrincipalType
from greenfield_python_sdk.protos.greenfield.sp import Status
from greenfield_python_sdk.protos.greenfield.storage import RedundancyType, VisibilityType


def set_message(url, message, broadcast_option: Optional[BroadcastOption] = None):
    if url == PUT_POLICY:
        if isinstance(message.statements[0].actions[0], int) == True:
            actions = []
            for i in message.statements[0].actions:
                actions.append(ActionType(i).name)
            message.statements[0].actions = actions
            message.statements[0].effect = Effect(message.statements[0].effect).name
            message.principal.type = PrincipalType(message.principal.type).name
            if message.expiration_time != None:
                message.expiration_time = message.expiration_time - timedelta(hours=9)

    if url == DELETE_POLICY:
        if isinstance(message.principal.type, int) == True:
            message.principal.type = PrincipalType(message.principal.type).name

    if url == CREATE_OBJECT:
        message.primary_sp_approval.sig = bytes(broadcast_option.sp_signature, "utf-8")
        message.expect_checksums = [bytes(checksum, "utf-8") for checksum in broadcast_option.checksums]

    if url == CREATE_BUCKET:
        message.primary_sp_approval.sig = bytes(broadcast_option.sp_signature, "utf-8")

    if url == MIGRATE_BUCKET:
        message.dst_primary_sp_approval.sig = bytes(broadcast_option.sp_signature, "utf-8")

    if url == VOTE:
        if isinstance(message.option, VoteOption) == True:
            message.option = VoteOption(message.option).name

    if url == UPDATE_SP_STATUS:
        if isinstance(message.status, Status) == True:
            message.status = Status(message.status).name
            message.duration = str(message.duration)

    if hasattr(message, "visibility"):
        if isinstance(message.visibility, VisibilityType) == True:
            message.visibility = message.visibility.name
        if isinstance(message.visibility, int) == True:
            message.visibility = VisibilityType(message.visibility).name

    if hasattr(message, "redundancy_type"):
        if isinstance(message.redundancy_type, RedundancyType) == True:
            message.redundancy_type = message.redundancy_type.name
        if isinstance(message.redundancy_type, int) == True:
            message.redundancy_type = RedundancyType(message.redundancy_type).name

    if url == COSMOS_GRANT:
        if message.grant.expiration and message.grant.expiration.hour == datetime.now().hour:
            message.grant.expiration = message.grant.expiration - timedelta(hours=9)

    if url == UPDATE_SP_STORAGE_PRICE and "." not in message.read_price:
        message.read_price = str(format(Decimal(message.read_price) / 10**18, ".18f"))
        message.store_price = str(format(Decimal(message.store_price) / 10**18, ".18f"))

    if url == EDIT_VALIDATOR and "." not in message.commission_rate and message.commission_rate != "":
        message.commission_rate = str(format(Decimal(message.commission_rate) / 10**18, ".18f"))
    return message


def decode_sp_approval(message, type_url: str):
    if type_url == CREATE_BUCKET:
        sp_approval = message.primary_sp_approval.sig
    elif type_url == CREATE_OBJECT:
        sp_approval = message.primary_sp_approval.sig
    elif type_url == MIGRATE_BUCKET:
        sp_approval = message.dst_primary_sp_approval.sig
    else:
        return message

    decoded_sp_approval = base64.b64decode(sp_approval)
    message.primary_sp_approval.sig = decoded_sp_approval
    return message


def rmv_unneeded_groups_type_index(type_url: str, message, tx_types: dict):
    if type_url == CREATE_GROUP and tx_types["Msg1"][3]["name"] == "members":
        del tx_types["Msg1"][3]
    if type_url == UPDATE_GROUP_MEMBER:
        if len(message.members_to_delete) == 0 and len(tx_types["Msg1"]) == 6:
            del tx_types["Msg1"][5]
        if len(message.members_to_add) == 0 and tx_types["Msg1"][4]["name"] == "members_to_add":
            del tx_types["Msg1"][4]
    return tx_types


def set_group_index_timestamp(message, final_message, type_url: str):
    if type_url == UPDATE_GROUP_MEMBER:
        if hasattr(message, "members_to_add"):
            for j, members in enumerate(final_message["members_to_add"]):
                members["expiration_time"] = message.members_to_add[j].expiration_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        if len(message.members_to_delete) == 0:
            final_message.pop("members_to_delete")
        if len(message.members_to_add) == 0:
            final_message.pop("members_to_add")

    if type_url == RENEW_GROUP_MEMBER:
        for j, members in enumerate(final_message["members"]):
            members["expiration_time"] = message.members[j].expiration_time.strftime("%Y-%m-%dT%H:%M:%SZ")

    return final_message


def set_value(base_type, obj, value):
    # Deserialize the raw value into the appropriate protobuf message
    instance = base_type.FromString(obj["value"])

    if obj["type"] == CREATE_VALIDATOR:
        instance.pubkey.value = binascii.unhexlify((instance.pubkey.value).hex()[4:])

    # Convert the protobuf message to its JSON representation
    if obj["type"] == STAKE_AUTHORIZATION:
        value = {
            "@type": obj["type"],
            **json.loads(instance.to_json(casing=Casing.SNAKE, include_default_values=False)),
        }
    else:
        value = {
            "@type": obj["type"],
            **json.loads(instance.to_json(casing=Casing.SNAKE, include_default_values=True)),
        }

    if obj["type"] == CREATE_STORAGE_PROVIDER:
        value["read_price"] = str(format(Decimal(value["read_price"]) / 10**18, ".18f"))
        value["store_price"] = str(format(Decimal(value["store_price"]) / 10**18, ".18f"))

    if obj["type"] == CREATE_VALIDATOR:
        pubkey = {"@type": value["pubkey"]["type_url"], "key": value["pubkey"]["value"]}
        value["pubkey"] = pubkey
        value["commission"]["max_rate"] = str(format(int(value["commission"]["max_rate"]) / 10**18, ".18f"))
        value["commission"]["max_change_rate"] = str(
            format(Decimal(value["commission"]["max_change_rate"]) / 10**18, ".18f")
        )
        value["commission"]["rate"] = str(format(Decimal(value["commission"]["rate"]), ".18f"))
    return value
