import base64
import binascii
import json
import re
from datetime import datetime, timedelta
from decimal import Decimal
from logging import getLogger
from typing import Any, Dict, List, Optional, Union

from betterproto import Casing
from eth_abi import encode as encode_abi
from eth_account import Account
from eth_typing import Hash32, HexStr
from hexbytes import HexBytes
from pydantic import BaseModel
from sha3 import keccak_256

from greenfield_python_sdk.__version__ import __version__
from greenfield_python_sdk.key_manager import KeyManager
from greenfield_python_sdk.models.eip712_messages import TYPES_MAP, URL_TO_PROTOS_TYPE_MAP
from greenfield_python_sdk.models.eip712_messages.base import BASE_TYPES
from greenfield_python_sdk.models.eip712_messages.group.group_url import (
    CREATE_GROUP,
    RENEW_GROUP_MEMEBER,
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
from greenfield_python_sdk.models.storage_provider import Any
from greenfield_python_sdk.models.transaction import BroadcastOption
from greenfield_python_sdk.protos.cosmos.gov.v1 import VoteOption
from greenfield_python_sdk.protos.cosmos.tx.v1beta1 import Tx
from greenfield_python_sdk.protos.greenfield.permission import ActionType, Effect, PrincipalType
from greenfield_python_sdk.protos.greenfield.sp import Status
from greenfield_python_sdk.protos.greenfield.storage import RedundancyType, VisibilityType

IGNORED_TYPES = [
    "PRINCIPAL_TYPE_UNSPECIFIED",
    "PRINCIPAL_TYPE_GNFD_ACCOUNT",
    "PRINCIPAL_TYPE_GNFD_GROUP",
]

logger = getLogger(__name__)


def fast_keccak(value: bytes) -> bytes:
    """
    Calculates ethereum keccak256 using fast library `pysha3`
    :param value:
    :return: Keccak256 used by ethereum as `bytes`
    """
    return keccak_256(value).digest()


def encode_data(primary_type: str, data, types):
    """
    Encode structured data as per Ethereum's signTypeData_v4.

    https://docs.metamask.io/guide/signing-data.html#sign-typed-data-v4

    This code is ported from the Javascript "eth-sig-util" package.
    """
    encoded_types = ["bytes32"]
    encoded_values = [hash_type(primary_type, types)]

    def _encode_field(name, typ, value):
        if typ in types:
            if value is None:
                return [
                    "bytes32",
                    "0x0000000000000000000000000000000000000000000000000000000000000000",
                ]
            else:
                return ["bytes32", fast_keccak(encode_data(typ, value, types))]

        if value is None:
            raise Exception(f"Missing value for field {name} of type {type}")

        # Accept string bytes
        if "bytes" in typ and isinstance(value, str):
            value = HexBytes(value)

        # Accept string uint and int
        if "int" in typ and isinstance(value, str):
            value = int(value)

        if typ == "bytes":
            return ["bytes32", fast_keccak(value)]

        if typ == "string":
            # Convert string to bytes.
            value = value.encode("utf-8")
            return ["bytes32", fast_keccak(value)]

        if typ.endswith("]"):
            # Array type
            if value:
                parsed_type = typ[: typ.rindex("[")]
                type_value_pairs = [_encode_field(name, parsed_type, v) for v in value]
                data_types, data_hashes = zip(*type_value_pairs)
            else:
                # Empty array
                data_types, data_hashes = [], []

            h = fast_keccak(encode_abi(data_types, data_hashes))
            return ["bytes32", h]

        return [typ, value]

    for field in types[primary_type]:
        try:
            typ, val = _encode_field(field["name"], field["type"], data[field["name"]])
            encoded_types.append(typ)
            encoded_values.append(val)
        except Exception as e:
            if field["name"] not in ["resources"]:
                logger.exception(e)

    return encode_abi(encoded_types, encoded_values)


def encode_type(primary_type: str, types) -> str:
    result = ""
    deps = find_type_dependencies(primary_type, types)
    deps = sorted([d for d in deps if d != primary_type])
    deps = [primary_type] + deps
    for typ in deps:
        children = types[typ]
        if not children:
            raise Exception(f"No type definition specified: {type}")

        defs = [f"{t['type']} {t['name']}" for t in types[typ]]
        result += typ + "(" + ",".join(defs) + ")"
    return result


def find_type_dependencies(primary_type: str, types, results=None):
    if results is None:
        results = []

    primary_type = re.split(r"\W", primary_type)[0]
    if primary_type in results or not types.get(primary_type):
        return results
    results.append(primary_type)

    for field in types[primary_type]:
        deps = find_type_dependencies(field["type"], types, results)
        for dep in deps:
            if dep not in results:
                results.append(dep)

    return results


def hash_type(primary_type: str, types) -> Hash32:
    return fast_keccak(encode_type(primary_type, types).encode())


def hash_struct(primary_type: str, data, types) -> Hash32:
    return fast_keccak(encode_data(primary_type, data, types))


def eip712_encode(typed_data: Dict[str, Any]) -> List[bytes]:
    """
    Given a dict of structured data and types, return a 3-element list of
    the encoded, signable data.

      0: The magic & version (0x1901)
      1: The encoded types
      2: The encoded data
    """
    try:
        parts = [
            bytes.fromhex("1901"),
            hash_struct("EIP712Domain", typed_data["domain"], typed_data["types"]),
        ]
        if typed_data["primaryType"] != "EIP712Domain":
            parts.append(
                hash_struct(
                    typed_data["primaryType"],
                    typed_data["message"],
                    typed_data["types"],
                )
            )
        return parts
    except (KeyError, AttributeError, TypeError, IndexError) as exc:
        raise ValueError(f"Not valid {typed_data}; Error at --> {exc}") from exc


def eip712_encode_hash(typed_data: Dict[str, Any]) -> Hash32:
    """
    :param typed_data: EIP712 structured data and types
    :return: Keccak256 hash of encoded signable data
    """
    return fast_keccak(b"".join(eip712_encode(typed_data)))


def eip712_signature(hashed_payload: bytes, private_key: Union[HexStr, bytes]) -> bytes:
    """
    Given a bytes object (fast_keccak hash from eip712_encode_hash) and a private key, return a signature suitable for
    EIP712 and EIP191 messages.
    """
    if isinstance(private_key, str) and private_key.startswith("0x"):
        private_key = private_key[2:]
    elif isinstance(private_key, bytes):
        private_key = private_key.hex()

    account = Account.from_key(private_key)
    signature = account.signHash(hashed_payload)["signature"]
    return signature


def deep_sort(obj):
    if isinstance(obj, dict):
        _sorted = {}
        for key in sorted(obj):
            _sorted[key] = deep_sort(obj[key])
        return _sorted
    elif isinstance(obj, list):
        return [deep_sort(elem) for elem in obj]
    else:
        return obj


def convert_value_to_json(obj) -> bytes:
    try:
        base_type = URL_TO_PROTOS_TYPE_MAP[obj["type"]]
    except KeyError:
        raise Exception(f"Unknown type: {obj['type']} - {obj}, add it to URL_TO_PROTOS_TYPE_MAP")

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

    value = set_value(obj, value)  # Assuming set_value is another function you've defined elsewhere

    # Convert the resulting value into a JSON string and then base64 encode it
    json_str = json.dumps(value, sort_keys=True).replace(": ", ":").replace(", ", ",")

    if obj["type"] == CREATE_STORAGE_PROVIDER or obj["type"] == CREATE_VALIDATOR:
        return json_str.encode()
    result = base64.b64encode(json_str.encode())
    return result


def set_value(obj, value):
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


def swap_any_value_to_json(obj):
    if isinstance(obj, dict):
        return {
            k: (
                convert_value_to_json(obj)
                if k == "value" and "type" in obj.keys() and obj["type"] not in IGNORED_TYPES
                else swap_any_value_to_json(v)
            )
            for k, v in obj.items()
        }
    elif isinstance(obj, list):
        return [swap_any_value_to_json(elem) for elem in obj]
    else:
        return obj


def swap_type_url_key(obj):
    if isinstance(obj, dict):
        return {("type" if k == "type_url" else k): swap_type_url_key(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [swap_type_url_key(elem) for elem in obj]
    else:
        return obj


class SignDocEip712(BaseModel):
    account_number: int
    chain_id: int
    fee: dict
    memo: str = ""
    msg1: dict
    sequence: int
    timeout_height: int


async def get_signature(
    key_manager: KeyManager, tx: Tx, message, chain_id: int, broadcast_option: Optional[BroadcastOption] = None
):
    tx_types = TYPES_MAP[tx.body.messages[0].type_url]

    if tx.body.messages[0].type_url == CREATE_GROUP and tx_types["Msg1"][3]["name"] == "members":
        del tx_types["Msg1"][3]

    if tx.body.messages[0].type_url == UPDATE_GROUP_MEMBER:
        if len(message.members_to_delete) == 0 and len(tx_types["Msg1"]) == 6:
            del tx_types["Msg1"][5]
        if len(message.members_to_add) == 0 and tx_types["Msg1"][4]["name"] == "members_to_add":
            del tx_types["Msg1"][4]

    full_types = {**BASE_TYPES, **tx_types}
    full_types = sorted_dict(full_types)
    message = set_message(tx.body.messages[0].type_url, message, broadcast_option)

    msg1 = {
        "type": tx.body.messages[0].type_url,  # Swaps the type_url key for the type key
        **message.to_pydict(casing=Casing.SNAKE, include_default_values=True),
    }
    # When a message has a "type_url" key, it needs to be swapped for a "type" key, this comes form "Any"/"AnyMessage" in the proto files
    msg1 = swap_type_url_key(msg1)

    # When a message has a "type_url" key, the "value" must be base64 encoded, not bytes. This comes from "Any"/"AnyMessage" in the proto files
    msg1 = swap_any_value_to_json(msg1)

    # Sorts the keys alphabetically in msg1
    msg1 = deep_sort(msg1)

    tx_message = SignDocEip712(
        **{
            "account_number": key_manager.account.account_number,
            "chain_id": str(chain_id),
            "fee": tx.auth_info.fee.to_pydict(casing=Casing.SNAKE, include_default_values=True),
            "memo": "",
            "msg1": msg1,
            "sequence": key_manager.account.next_sequence,
            "timeout_height": "0",
        }
    )
    if hasattr(message, "grant") and tx_message.msg1["grant"]["expiration"]:
        tx_message.msg1["grant"]["expiration"] = (
            message.grant.expiration.strftime("%Y-%m-%dT%H:%M:%S.%fZ") if message.grant.expiration.year > 2000 else ""
        )

    if tx.body.messages[0].type_url == UPDATE_GROUP_MEMBER:
        if hasattr(message, "members_to_add"):
            for i, members in enumerate(tx_message.msg1["members_to_add"]):
                members["expiration_time"] = message.members_to_add[i].expiration_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        if len(message.members_to_delete) == 0:
            tx_message.msg1.pop("members_to_delete")
        if len(message.members_to_add) == 0:
            tx_message.msg1.pop("members_to_add")

    if tx.body.messages[0].type_url == RENEW_GROUP_MEMEBER:
        for i, members in enumerate(tx_message.msg1["members"]):
            members["expiration_time"] = message.members[i].expiration_time.strftime("%Y-%m-%dT%H:%M:%SZ")

    if hasattr(message, "statements"):
        del tx_message.msg1["statements"][0]["limit_size"]
        if not tx_message.msg1["statements"][0]["resources"]:
            del tx_message.msg1["statements"][0]["resources"]
        tx_message.msg1["statements"][0]["expiration_time"] = ""
        tx_message.msg1["expiration_time"] = (
            message.expiration_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ") if message.expiration_time.year != 1969 else ""
        )

    payload = {
        "types": full_types,
        "primaryType": "Tx",
        "domain": {
            "name": "Greenfield Tx",
            "version": "1.0.0",
            "chainId": chain_id,
            "verifyingContract": "greenfield",
            "salt": "0",
        },
        "message": tx_message.model_dump(),
    }

    # Sort fees
    payload["message"]["fee"] = {k: v for k, v in sorted(payload["message"]["fee"].items())}
    payload["message"]["fee"]["amount"] = [
        {"amount": entry["amount"], "denom": entry["denom"]} for entry in payload["message"]["fee"]["amount"]
    ]
    eip712_hash = eip712_encode_hash(payload)
    signature = eip712_signature(eip712_hash, key_manager.private_key)
    signature = bytes.fromhex(signature.hex()[2:])
    return signature


def sorted_dict(full_types):
    # First, sort the main dictionary by its keys
    sorted_d = dict(sorted(full_types.items()))

    # For each key in the main dictionary, sort the nested list of dictionaries by the 'name' key
    for key, value in sorted_d.items():
        if isinstance(value, list) and all(isinstance(item, dict) and "name" in item for item in value):
            sorted_d[key] = sorted(value, key=lambda x: x["name"])
    return sorted_d


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
