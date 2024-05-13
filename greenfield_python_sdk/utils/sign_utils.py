import base64
import json
import re
from logging import getLogger
from typing import Any, Dict, List, Optional, Union

from betterproto import Casing
from eth_abi import encode as encode_abi
from eth_account import Account
from eth_typing import Hash32, HexStr
from hexbytes import HexBytes
from sha3 import keccak_256

from greenfield_python_sdk.__version__ import __version__
from greenfield_python_sdk.key_manager import KeyManager
from greenfield_python_sdk.models.eip712_messages import TYPES_MAP, URL_TO_PROTOS_TYPE_MAP
from greenfield_python_sdk.models.eip712_messages.base import BASE_TYPES
from greenfield_python_sdk.models.eip712_messages.sp.sp_url import CREATE_STORAGE_PROVIDER
from greenfield_python_sdk.models.eip712_messages.staking.staking_url import CREATE_VALIDATOR
from greenfield_python_sdk.models.storage_provider import Any
from greenfield_python_sdk.models.transaction import BroadcastOption
from greenfield_python_sdk.protos.cosmos.tx.v1beta1 import Tx
from greenfield_python_sdk.utils.type_url_exception_utils import (
    decode_sp_approval,
    rmv_unneeded_groups_type_index,
    set_group_index_timestamp,
    set_message,
    set_value,
)

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

    value = set_value(base_type, obj, value)
    # Convert the resulting value into a JSON string and then base64 encode it
    json_str = json.dumps(value, sort_keys=True).replace(": ", ":").replace(", ", ",")

    if obj["type"] == CREATE_STORAGE_PROVIDER or obj["type"] == CREATE_VALIDATOR:
        return json_str.encode()
    result = base64.b64encode(json_str.encode())
    return result


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


async def get_signatures(
    key_manager: KeyManager, tx: Tx, message, chain_id: int, broadcast_option: Optional[BroadcastOption] = None
):
    tx_type = {
        "Tx": [
            {"name": "account_number", "type": "uint256"},
            {"name": "chain_id", "type": "uint256"},
            {"name": "fee", "type": "Fee"},
            {"name": "memo", "type": "string"},
            {"name": "sequence", "type": "uint256"},
            {"name": "timeout_height", "type": "uint256"},
        ],
    }
    for i in range(0, len(message)):
        tx_type["Tx"].append({"name": f"msg{i+1}", "type": f"Msg{i+1}"})

    full_types = {**BASE_TYPES, **tx_type}
    tx_message = {
        "account_number": key_manager.account.account_number,
        "chain_id": str(chain_id),
        "fee": tx.auth_info.fee.to_pydict(casing=Casing.SNAKE, include_default_values=True),
        "memo": "",
        "sequence": key_manager.account.next_sequence,
        "timeout_height": "0",
    }

    all_messages, full_types = set_messages(tx.body.messages, message, full_types, broadcast_option)

    tx_message = tx_message | all_messages
    tx_message = deep_sort(tx_message)

    full_types = sorted_dict(full_types)

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
        "message": tx_message,
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


def set_messages(tx, message, full_types, broadcast_option: Optional[BroadcastOption] = None):
    all_messages = {}

    for i, message_url in enumerate(tx):
        tx_types = TYPES_MAP[message_url.type_url]
        tx_types = rmv_unneeded_groups_type_index(message_url.type_url, message[i], tx_types)

        if len(message) > 1 and i > 0:
            tx_types = {
                key.replace("Msg1", f"Msg{i+1}"): [
                    {**item, "type": item["type"].replace("Msg1", f"Msg{i+1}")} if "Msg1" in item["type"] else item
                    for item in value
                ]
                for key, value in tx_types.items()
                if "Msg1" in key
            }

        full_types = full_types | {**tx_types}

        message[i] = set_message(message_url.type_url, message[i], broadcast_option)
        msg = {
            "type": message_url.type_url,  # Swaps the type_url key for the type key
            **message[i].to_pydict(casing=Casing.SNAKE, include_default_values=True),
        }
        # When a message has a "type_url" key, it needs to be swapped for a "type" key, this comes form "Any"/"AnyMessage" in the proto files
        msg = swap_type_url_key(msg)

        # When a message has a "type_url" key, the "value" must be base64 encoded, not bytes. This comes from "Any"/"AnyMessage" in the proto files
        msg = swap_any_value_to_json(msg)

        # Sorts the keys alphabetically in msg1
        msg = deep_sort(msg)

        if hasattr(message[i], "grant") and msg["grant"]["expiration"]:
            msg["grant"]["expiration"] = (
                message[i].grant.expiration.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                if message[i].grant.expiration.year > 2000
                else ""
            )

        msg = set_group_index_timestamp(message[i], msg, message_url.type_url)

        if hasattr(message[i], "statements"):
            del msg["statements"][0]["limit_size"]
            if not msg["statements"][0]["resources"]:
                del msg["statements"][0]["resources"]
            msg["statements"][0]["expiration_time"] = ""
            msg["expiration_time"] = (
                message[i].expiration_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                if message[i].expiration_time.year != 1969
                else ""
            )

        all_messages = all_messages | {f"msg{i+1}": msg}
    return all_messages, full_types


def sorted_dict(full_types):
    # First, sort the main dictionary by its keys
    sorted_d = dict(sorted(full_types.items()))

    # For each key in the main dictionary, sort the nested list of dictionaries by the 'name' key
    for key, value in sorted_d.items():
        if isinstance(value, list) and all(isinstance(item, dict) and "name" in item for item in value):
            sorted_d[key] = sorted(value, key=lambda x: x["name"])
    return sorted_d


def encode_sp_approval_message(messages, type_urls):
    encoded_messages = []
    for message, type_url in zip(messages, type_urls):
        encoded_message = decode_sp_approval(message, type_url)
        encoded_messages.append(encoded_message)
    return encoded_messages
