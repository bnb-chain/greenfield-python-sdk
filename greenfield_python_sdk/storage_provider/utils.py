import ctypes
import hashlib
import io
import json
import os
import re
import string
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlencode, urljoin

import coincurve
from Crypto.Hash import keccak

from greenfield_python_sdk.key_manager import KeyManager
from greenfield_python_sdk.models.const import AUTH_V1, ETH_ADDRESS_LENGTH, SIGN_ALGORITHM, SUPPORT_HEADERS
from greenfield_python_sdk.models.object import ObjectStat
from greenfield_python_sdk.protos.greenfield.storage import RedundancyType


def sign_message(message, key_manager: KeyManager):
    unsigned_message_string = bytes(message, "utf-8")
    sha256_hash = hashlib.sha256(unsigned_message_string)
    sha256_bytes = sha256_hash.digest()
    keccak_hash = keccak.new(digest_bits=256, data=sha256_bytes).digest()

    privkey = coincurve.PrivateKey(key_manager.account.private_key)
    signature = privkey.sign_recoverable(keccak_hash, hasher=None)

    return keccak_hash, signature


async def generate_authorization_header(metadata: dict, key_manager: KeyManager, headers: dict):
    unsigned_msg_string = f"{metadata['method']}\n{metadata['relative_path']}\n{metadata['query_str'][1:]}"
    h = ""
    for head in list(headers.keys()):
        if head in SUPPORT_HEADERS:
            unsigned_msg_string += "\n" + head.lower() + ":" + headers[head]
            h += head.lower() + ";"
    unsigned_msg_string += f"\n{metadata['base_url'][8:]}\n\n" + h[:-1]

    keccak_hash, signedMsg = sign_message(unsigned_msg_string, key_manager)
    signed_msg_string = ", ".join(
        [f"{AUTH_V1} {SIGN_ALGORITHM}", f"SignedMsg={keccak_hash.hex()}", f"Signature={signedMsg.hex()}"]
    )

    return signed_msg_string


def get_unsigned_bytes_from_message(message) -> bytes:
    message_dict = message.to_dict()
    json_str = json.dumps(message_dict, separators=(",", ":"), sort_keys=True)

    return bytes(json_str, "utf-8")


def check_valid_bucket_name(bucket_name: str):
    valid_bucket_name = re.compile(r"^[a-z0-9][a-z0-9\.\-]{1,61}[a-z0-9]$")
    ip_address = re.compile(r"^(\d+\.){3}\d+$")

    if len(bucket_name) == 0 or bucket_name.strip() == "":
        raise ValueError("Bucket name cannot be empty")
    if len(bucket_name) < 3:
        raise ValueError("Bucket name cannot be shorter than 3 characters")
    if len(bucket_name) > 63:
        raise ValueError("Bucket name cannot be longer than 63 characters")
    if ip_address.match(bucket_name):
        raise ValueError("Bucket name cannot be an IP address")
    if ".." in bucket_name or ".-" in bucket_name or "-." in bucket_name:
        raise ValueError("Bucket name contains invalid characters")
    if not valid_bucket_name.match(bucket_name):
        raise ValueError("Bucket name contains invalid characters")


def check_valid_object_name(object_name: str):
    if len(object_name) == 0 or object_name.strip() == "":
        raise ValueError("Object name cannot be empty")
    if len(object_name) > 1024:
        raise ValueError("Object name cannot be longer than 1024 characters")
    if ".." in object_name in object_name:
        raise ValueError("Object name with a bad path component is not supported")
    if not is_utf8_string(object_name):
        raise ValueError("Object name with non UTF-8 strings is not supported")
    if "//" in object_name:
        raise ValueError('Object name containing "//" is not supported')


def check_address(address: str) -> str:
    if len(address) == 0:
        raise ValueError("Empty hex address")
    if address[:2] != "0x":
        raise ValueError("Invalid hex address prefix: {}".format(address[:2]))
    if len(address[2:]) != 2 * ETH_ADDRESS_LENGTH:
        raise ValueError("Invalid address hex length: {} != {}".format(len(address[2:]), 2 * ETH_ADDRESS_LENGTH))
    return address


def is_valid_object_prefix(prefix) -> bool:
    if ".." in prefix or "." in prefix:
        raise ValueError("invalid object prefix")
    if not all(c in string.printable for c in prefix):
        raise ValueError("invalid object prefix")
    if "//" in prefix:
        raise ValueError("invalid object prefix")
    return True


def create_example_object() -> io.BytesIO:
    buffer = io.StringIO()
    line = "1234567890,1234567890,1234567890,1234567890,1234567890,1234567890,1234567890,1234567890,1234567890"
    for i in range(2 * 1):
        buffer.write(f"[{i:05d}] {line}\n")

    content = buffer.getvalue()
    buffer.close()
    return io.BytesIO(content.encode("utf-8"))


def generate_url(
    base_url: str,
    bucket_name: Optional[str] = None,
    object_name: Optional[str] = None,
    endpoint: Optional[str] = None,
    query_parameters: Optional[Dict[str, str]] = {},
    is_admin_api: Optional[bool] = False,
) -> str:
    prefix = "/greenfield/admin/v1/" if is_admin_api else "/"

    url = urljoin(base_url, prefix)
    if bucket_name:
        url = urljoin(url, bucket_name)
    if object_name:
        url = urljoin(url, object_name)
    url = urljoin(url, endpoint)
    url += "?" + urlencode(query_parameters) if query_parameters else ""

    return url


def generate_url_chunks(
    bucket_name: Optional[str] = None,
    object_name: Optional[str] = None,
    endpoint: Optional[str] = None,
    query_parameters: Optional[Dict[str, str]] = {},
    is_admin_api: Optional[bool] = False,
) -> str:
    prefix = "/greenfield/admin/v1/" if is_admin_api else "/"

    relative_path = prefix
    if bucket_name:
        relative_path = urljoin(relative_path, bucket_name)
    if object_name:
        relative_path = urljoin(relative_path, object_name)

    relative_path = urljoin(relative_path, endpoint)
    query_str = "?" + urlencode(query_parameters) if query_parameters else ""

    return relative_path, query_str


def is_utf8_string(object_name):
    try:
        object_name.encode("utf-8").decode("utf-8")
    except UnicodeDecodeError:
        return False
    else:
        return True


async def generate_headers(metadata, key_manager: KeyManager) -> Dict[str, str]:
    headers = {}

    if metadata["txn_msg"]:
        headers["X-Gnfd-Unsigned-Msg"] = metadata["txn_msg"].decode()

    if metadata["user_address"]:
        headers["X-Gnfd-User-Address"] = metadata["user_address"]

    if metadata["content_length"]:
        headers["Content-Length"] = str(metadata["content_length"])

    if metadata["content_type"]:
        headers["Content-Type"] = metadata["content_type"]

    headers["Authorization"] = await generate_authorization_header(metadata, key_manager, headers)

    return headers


def get_obj_info(object_name: str, http_response) -> ObjectStat:
    content_length = http_response.headers.get("Content-Length") or 0
    content_type = http_response.headers.get("Content-Type")
    if content_type == "":
        content_type = "application/octet-stream"

    return ObjectStat(
        object_name=object_name,
        content_type=content_type,
        size=int(content_length),
    )


def compute_integrity_hash_go(
    reader, segment_size: int, data_shards: int, parity_shards: int
) -> Tuple[List[bytes], int, RedundancyType]:
    dir_path = getDirPath()
    value = reader.getvalue()
    content_lenght = len(value)
    data_redundancy = ctypes.cdll.LoadLibrary(dir_path).GenerateDataRedundancy

    c_data = ctypes.c_char_p(value)
    data_redundancy.argtypes = [
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_char_p,
    ]
    data_redundancy.restype = ctypes.c_void_p

    data_redundancy_output = ctypes.string_at(
        data_redundancy(segment_size, data_shards, parity_shards, content_lenght, c_data), 224
    )

    part_size = len(data_redundancy_output) // 7
    parts = [data_redundancy_output[i * part_size : (i + 1) * part_size] for i in range(7)]

    return parts, content_lenght, RedundancyType.REDUNDANCY_EC_TYPE


def getDirPath():
    return (
        os.path.dirname(os.path.realpath(__file__)) + "/../go_library/main.dll"
        if os.name == "nt"
        else os.path.dirname(os.path.realpath(__file__)) + "/../go_library/main.so"
    )
