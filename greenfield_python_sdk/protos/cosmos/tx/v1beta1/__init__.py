# Generated by the protocol buffer compiler.  DO NOT EDIT!
# sources: cosmos/tx/v1beta1/service.proto, cosmos/tx/v1beta1/tx.proto
# plugin: python-betterproto
# This file has been @generated
import warnings
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dataclasses import dataclass
else:
    from pydantic.dataclasses import dataclass

from typing import TYPE_CHECKING, Dict, List, Optional

import betterproto
import betterproto.lib.google.protobuf as betterproto_lib_google_protobuf
import grpclib
from betterproto.grpc.grpclib_server import ServiceBase
from pydantic import root_validator

from ....tendermint import types as ___tendermint_types__
from ...base import v1beta1 as __base_v1_beta1__
from ...base.abci import v1beta1 as __base_abci_v1_beta1__
from ...base.query import v1beta1 as __base_query_v1_beta1__
from ...crypto.multisig import v1beta1 as __crypto_multisig_v1_beta1__
from ..signing import v1beta1 as _signing_v1_beta1__

if TYPE_CHECKING:
    import grpclib.server
    from betterproto.grpc.grpclib_client import MetadataLike
    from grpclib.metadata import Deadline


class OrderBy(betterproto.Enum):
    """OrderBy defines the sorting order"""

    ORDER_BY_UNSPECIFIED = 0
    """
    ORDER_BY_UNSPECIFIED specifies an unknown sorting order. OrderBy defaults
    to ASC in this case.
    """

    ORDER_BY_ASC = 1
    """ORDER_BY_ASC defines ascending order"""

    ORDER_BY_DESC = 2
    """ORDER_BY_DESC defines descending order"""


class BroadcastMode(betterproto.Enum):
    """
    BroadcastMode specifies the broadcast mode for the TxService.Broadcast RPC
    method.
    """

    BROADCAST_MODE_UNSPECIFIED = 0
    """zero-value for mode ordering"""

    BROADCAST_MODE_BLOCK = 1
    """
    DEPRECATED: use BROADCAST_MODE_SYNC instead, BROADCAST_MODE_BLOCK is not
    supported by the SDK from v0.47.x onwards.
    """

    BROADCAST_MODE_SYNC = 2
    """
    BROADCAST_MODE_SYNC defines a tx broadcasting mode where the client waits
    for a CheckTx execution response only.
    """

    BROADCAST_MODE_ASYNC = 3
    """
    BROADCAST_MODE_ASYNC defines a tx broadcasting mode where the client
    returns immediately.
    """


@dataclass(eq=False, repr=False)
class Tx(betterproto.Message):
    """Tx is the standard type used for broadcasting transactions."""

    body: "TxBody" = betterproto.message_field(1)
    """body is the processable content of the transaction"""

    auth_info: "AuthInfo" = betterproto.message_field(2)
    """
    auth_info is the authorization related content of the transaction,
    specifically signers, signer modes and fee
    """

    signatures: List[bytes] = betterproto.bytes_field(3)
    """
    signatures is a list of signatures that matches the length and order of
    AuthInfo's signer_infos to allow connecting signature meta information like
    public key and signing mode by position.
    """


@dataclass(eq=False, repr=False)
class TxRaw(betterproto.Message):
    """
    TxRaw is a variant of Tx that pins the signer's exact binary representation
    of body and auth_info. This is used for signing, broadcasting and
    verification. The binary `serialize(tx: TxRaw)` is stored in Tendermint and
    the hash `sha256(serialize(tx: TxRaw))` becomes the "txhash", commonly used
    as the transaction ID.
    """

    body_bytes: bytes = betterproto.bytes_field(1)
    """
    body_bytes is a protobuf serialization of a TxBody that matches the
    representation in SignDoc.
    """

    auth_info_bytes: bytes = betterproto.bytes_field(2)
    """
    auth_info_bytes is a protobuf serialization of an AuthInfo that matches the
    representation in SignDoc.
    """

    signatures: List[bytes] = betterproto.bytes_field(3)
    """
    signatures is a list of signatures that matches the length and order of
    AuthInfo's signer_infos to allow connecting signature meta information like
    public key and signing mode by position.
    """


@dataclass(eq=False, repr=False)
class SignDoc(betterproto.Message):
    """
    SignDoc is the type used for generating sign bytes for SIGN_MODE_DIRECT.
    """

    body_bytes: bytes = betterproto.bytes_field(1)
    """
    body_bytes is protobuf serialization of a TxBody that matches the
    representation in TxRaw.
    """

    auth_info_bytes: bytes = betterproto.bytes_field(2)
    """
    auth_info_bytes is a protobuf serialization of an AuthInfo that matches the
    representation in TxRaw.
    """

    chain_id: str = betterproto.string_field(3)
    """
    chain_id is the unique identifier of the chain this transaction targets. It
    prevents signed transactions from being used on another chain by an
    attacker
    """

    account_number: int = betterproto.uint64_field(4)
    """account_number is the account number of the account in state"""


@dataclass(eq=False, repr=False)
class SignDocDirectAux(betterproto.Message):
    """
    SignDocDirectAux is the type used for generating sign bytes for
    SIGN_MODE_DIRECT_AUX. Since: cosmos-sdk 0.46
    """

    body_bytes: bytes = betterproto.bytes_field(1)
    """
    body_bytes is protobuf serialization of a TxBody that matches the
    representation in TxRaw.
    """

    public_key: "betterproto_lib_google_protobuf.Any" = betterproto.message_field(2)
    """public_key is the public key of the signing account."""

    chain_id: str = betterproto.string_field(3)
    """
    chain_id is the identifier of the chain this transaction targets. It
    prevents signed transactions from being used on another chain by an
    attacker.
    """

    account_number: int = betterproto.uint64_field(4)
    """account_number is the account number of the account in state."""

    sequence: int = betterproto.uint64_field(5)
    """sequence is the sequence number of the signing account."""

    tip: "Tip" = betterproto.message_field(6)
    """
    Tip is the optional tip used for transactions fees paid in another denom.
    It should be left empty if the signer is not the tipper for this
    transaction. This field is ignored if the chain didn't enable tips, i.e.
    didn't add the `TipDecorator` in its posthandler.
    """


@dataclass(eq=False, repr=False)
class SignDocEip712(betterproto.Message):
    """
    SignDocEIP712 is the type used for generating sign bytes for
    SIGN_MODE_EIP_712.
    """

    chain_id: int = betterproto.uint64_field(1)
    """
    chain_id is the identifier of the chain this transaction targets. It
    prevents signed transactions from being used on another chain by an
    attacker.
    """

    account_number: int = betterproto.uint64_field(2)
    """account_number is the account number of the account in state."""

    sequence: int = betterproto.uint64_field(3)
    """sequence is the sequence number of the signing account."""

    fee: "Fee" = betterproto.message_field(4)
    """
    Fee is the fee and gas limit for the transaction. The first signer is the
    primary signer and the one which pays the fee. The fee can be calculated
    based on the cost of evaluating the body and doing signature verification
    of the signers. This can be estimated via simulation.
    """

    msgs: List["betterproto_lib_google_protobuf.Any"] = betterproto.message_field(5)
    """msg is the msg in the EIP712 transaction."""

    timeout_height: int = betterproto.uint64_field(6)
    """timeout_height is the transaction's timeout height (if set)."""

    memo: str = betterproto.string_field(7)
    """
    memo is any arbitrary note/comment to be added to the transaction. WARNING:
    in clients, any publicly exposed text should not be called memo, but should
    be called `note` instead (see https://github.com/cosmos/cosmos-
    sdk/issues/9122).
    """

    tip: "Tip" = betterproto.message_field(8)
    """
    Tip is the optional tip used for transactions fees paid in another denom.
    It should be left empty if the signer is not the tipper for this
    transaction. This field is ignored if the chain didn't enable tips, i.e.
    didn't add the `TipDecorator` in its posthandler.
    """


@dataclass(eq=False, repr=False)
class TxBody(betterproto.Message):
    """TxBody is the body of a transaction that all signers sign over."""

    messages: List["betterproto_lib_google_protobuf.Any"] = betterproto.message_field(1)
    """
    messages is a list of messages to be executed. The required signers of
    those messages define the number and order of elements in AuthInfo's
    signer_infos and Tx's signatures. Each required signer address is added to
    the list only the first time it occurs. By convention, the first required
    signer (usually from the first message) is referred to as the primary
    signer and pays the fee for the whole transaction.
    """

    memo: str = betterproto.string_field(2)
    """
    memo is any arbitrary note/comment to be added to the transaction. WARNING:
    in clients, any publicly exposed text should not be called memo, but should
    be called `note` instead (see https://github.com/cosmos/cosmos-
    sdk/issues/9122).
    """

    timeout_height: int = betterproto.uint64_field(3)
    """
    timeout is the block height after which this transaction will not be
    processed by the chain
    """

    extension_options: List["betterproto_lib_google_protobuf.Any"] = betterproto.message_field(1023)
    """
    extension_options are arbitrary options that can be added by chains when
    the default options are not sufficient. If any of these are present and
    can't be handled, the transaction will be rejected
    """

    non_critical_extension_options: List["betterproto_lib_google_protobuf.Any"] = betterproto.message_field(2047)
    """
    extension_options are arbitrary options that can be added by chains when
    the default options are not sufficient. If any of these are present and
    can't be handled, they will be ignored
    """


@dataclass(eq=False, repr=False)
class AuthInfo(betterproto.Message):
    """
    AuthInfo describes the fee and signer modes that are used to sign a
    transaction.
    """

    signer_infos: List["SignerInfo"] = betterproto.message_field(1)
    """
    signer_infos defines the signing modes for the required signers. The number
    and order of elements must match the required signers from TxBody's
    messages. The first element is the primary signer and the one which pays
    the fee.
    """

    fee: "Fee" = betterproto.message_field(2)
    """
    Fee is the fee and gas limit for the transaction. The first signer is the
    primary signer and the one which pays the fee. The fee can be calculated
    based on the cost of evaluating the body and doing signature verification
    of the signers. This can be estimated via simulation.
    """

    tip: "Tip" = betterproto.message_field(3)
    """
    Tip is the optional tip used for transactions fees paid in another denom.
    This field is ignored if the chain didn't enable tips, i.e. didn't add the
    `TipDecorator` in its posthandler. Since: cosmos-sdk 0.46
    """


@dataclass(eq=False, repr=False)
class SignerInfo(betterproto.Message):
    """
    SignerInfo describes the public key and signing mode of a single top-level
    signer.
    """

    public_key: "betterproto_lib_google_protobuf.Any" = betterproto.message_field(1)
    """
    public_key is the public key of the signer. It is optional for accounts
    that already exist in state. If unset, the verifier can use the required \
    signer address for this position and lookup the public key.
    """

    mode_info: "ModeInfo" = betterproto.message_field(2)
    """
    mode_info describes the signing mode of the signer and is a nested
    structure to support nested multisig pubkey's
    """

    sequence: int = betterproto.uint64_field(3)
    """
    sequence is the sequence of the account, which describes the number of
    committed transactions signed by a given address. It is used to prevent
    replay attacks.
    """


@dataclass(eq=False, repr=False)
class ModeInfo(betterproto.Message):
    """
    ModeInfo describes the signing mode of a single or nested multisig signer.
    """

    single: Optional["ModeInfoSingle"] = betterproto.message_field(1, optional=True, group="sum")
    """single represents a single signer"""

    multi: Optional["ModeInfoMulti"] = betterproto.message_field(2, optional=True, group="sum")
    """multi represents a nested multisig signer"""

    @root_validator()
    def check_oneof(cls, values):
        return cls._validate_field_groups(values)


@dataclass(eq=False, repr=False)
class ModeInfoSingle(betterproto.Message):
    """
    Single is the mode info for a single signer. It is structured as a message
    to allow for additional fields such as locale for SIGN_MODE_TEXTUAL in the
    future
    """

    mode: "_signing_v1_beta1__.SignMode" = betterproto.enum_field(1)
    """mode is the signing mode of the single signer"""


@dataclass(eq=False, repr=False)
class ModeInfoMulti(betterproto.Message):
    """Multi is the mode info for a multisig public key"""

    bitarray: "__crypto_multisig_v1_beta1__.CompactBitArray" = betterproto.message_field(1)
    """bitarray specifies which keys within the multisig are signing"""

    mode_infos: List["ModeInfo"] = betterproto.message_field(2)
    """
    mode_infos is the corresponding modes of the signers of the multisig which
    could include nested multisig public keys
    """


@dataclass(eq=False, repr=False)
class Fee(betterproto.Message):
    """
    Fee includes the amount of coins paid in fees and the maximum gas to be
    used by the transaction. The ratio yields an effective "gasprice", which
    must be above some miminum to be accepted into the mempool.
    """

    amount: List["__base_v1_beta1__.Coin"] = betterproto.message_field(1)
    """amount is the amount of coins to be paid as a fee"""

    gas_limit: int = betterproto.uint64_field(2)
    """
    gas_limit is the maximum gas that can be used in transaction processing
    before an out of gas error occurs
    """

    payer: str = betterproto.string_field(3)
    """
    if unset, the first signer is responsible for paying the fees. If set, the
    specified account must pay the fees. the payer must be a tx signer (and
    thus have signed this field in AuthInfo). setting this field does *not*
    change the ordering of required signers for the transaction.
    """

    granter: str = betterproto.string_field(4)
    """
    if set, the fee payer (either the first signer or the value of the payer
    field) requests that a fee grant be used to pay fees instead of the fee
    payer's own balance. If an appropriate fee grant does not exist or the
    chain does not support fee grants, this will fail
    """


@dataclass(eq=False, repr=False)
class Tip(betterproto.Message):
    """Tip is the tip used for meta-transactions. Since: cosmos-sdk 0.46"""

    amount: List["__base_v1_beta1__.Coin"] = betterproto.message_field(1)
    """amount is the amount of the tip"""

    tipper: str = betterproto.string_field(2)
    """tipper is the address of the account paying for the tip"""


@dataclass(eq=False, repr=False)
class AuxSignerData(betterproto.Message):
    """
    AuxSignerData is the intermediary format that an auxiliary signer (e.g. a
    tipper) builds and sends to the fee payer (who will build and broadcast the
    actual tx). AuxSignerData is not a valid tx in itself, and will be rejected
    by the node if sent directly as-is. Since: cosmos-sdk 0.46
    """

    address: str = betterproto.string_field(1)
    """
    address is the bech32-encoded address of the auxiliary signer. If using
    AuxSignerData across different chains, the bech32 prefix of the target
    chain (where the final transaction is broadcasted) should be used.
    """

    sign_doc: "SignDocDirectAux" = betterproto.message_field(2)
    """
    sign_doc is the SIGN_MODE_DIRECT_AUX sign doc that the auxiliary signer
    signs. Note: we use the same sign doc even if we're signing with
    LEGACY_AMINO_JSON.
    """

    mode: "_signing_v1_beta1__.SignMode" = betterproto.enum_field(3)
    """mode is the signing mode of the single signer."""

    sig: bytes = betterproto.bytes_field(4)
    """sig is the signature of the sign doc."""


@dataclass(eq=False, repr=False)
class GetTxsEventRequest(betterproto.Message):
    """
    GetTxsEventRequest is the request type for the Service.TxsByEvents RPC
    method.
    """

    events: List[str] = betterproto.string_field(1)
    """events is the list of transaction event type."""

    pagination: "__base_query_v1_beta1__.PageRequest" = betterproto.message_field(2)
    """
    pagination defines a pagination for the request. Deprecated post v0.46.x:
    use page and limit instead.
    """

    order_by: "OrderBy" = betterproto.enum_field(3)
    page: int = betterproto.uint64_field(4)
    """
    page is the page number to query, starts at 1. If not provided, will
    default to first page.
    """

    limit: int = betterproto.uint64_field(5)
    """
    limit is the total number of results to be returned in the result page. If
    left empty it will default to a value to be set by each app.
    """

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.is_set("pagination"):
            warnings.warn("GetTxsEventRequest.pagination is deprecated", DeprecationWarning)


@dataclass(eq=False, repr=False)
class GetTxsEventResponse(betterproto.Message):
    """
    GetTxsEventResponse is the response type for the Service.TxsByEvents RPC
    method.
    """

    txs: List["Tx"] = betterproto.message_field(1)
    """txs is the list of queried transactions."""

    tx_responses: List["__base_abci_v1_beta1__.TxResponse"] = betterproto.message_field(2)
    """tx_responses is the list of queried TxResponses."""

    pagination: "__base_query_v1_beta1__.PageResponse" = betterproto.message_field(3)
    """
    pagination defines a pagination for the response. Deprecated post v0.46.x:
    use total instead.
    """

    total: int = betterproto.uint64_field(4)
    """total is total number of results available"""

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.is_set("pagination"):
            warnings.warn("GetTxsEventResponse.pagination is deprecated", DeprecationWarning)


@dataclass(eq=False, repr=False)
class BroadcastTxRequest(betterproto.Message):
    """
    BroadcastTxRequest is the request type for the Service.BroadcastTxRequest
    RPC method.
    """

    tx_bytes: bytes = betterproto.bytes_field(1)
    """tx_bytes is the raw transaction."""

    mode: "BroadcastMode" = betterproto.enum_field(2)


@dataclass(eq=False, repr=False)
class BroadcastTxResponse(betterproto.Message):
    """
    BroadcastTxResponse is the response type for the Service.BroadcastTx
    method.
    """

    tx_response: "__base_abci_v1_beta1__.TxResponse" = betterproto.message_field(1)
    """tx_response is the queried TxResponses."""


@dataclass(eq=False, repr=False)
class SimulateRequest(betterproto.Message):
    """
    SimulateRequest is the request type for the Service.Simulate RPC method.
    """

    tx: "Tx" = betterproto.message_field(1)
    """
    tx is the transaction to simulate. Deprecated. Send raw tx bytes instead.
    """

    tx_bytes: bytes = betterproto.bytes_field(2)
    """tx_bytes is the raw transaction. Since: cosmos-sdk 0.43"""

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.is_set("tx"):
            warnings.warn("SimulateRequest.tx is deprecated", DeprecationWarning)


@dataclass(eq=False, repr=False)
class SimulateResponse(betterproto.Message):
    """
    SimulateResponse is the response type for the Service.SimulateRPC method.
    """

    gas_info: "__base_abci_v1_beta1__.GasInfo" = betterproto.message_field(1)
    """gas_info is the information about gas used in the simulation."""

    result: "__base_abci_v1_beta1__.Result" = betterproto.message_field(2)
    """result is the result of the simulation."""


@dataclass(eq=False, repr=False)
class GetTxRequest(betterproto.Message):
    """GetTxRequest is the request type for the Service.GetTx RPC method."""

    hash: str = betterproto.string_field(1)
    """hash is the tx hash to query, encoded as a hex string."""


@dataclass(eq=False, repr=False)
class GetTxResponse(betterproto.Message):
    """GetTxResponse is the response type for the Service.GetTx method."""

    tx: "Tx" = betterproto.message_field(1)
    """tx is the queried transaction."""

    tx_response: "__base_abci_v1_beta1__.TxResponse" = betterproto.message_field(2)
    """tx_response is the queried TxResponses."""


@dataclass(eq=False, repr=False)
class GetBlockWithTxsRequest(betterproto.Message):
    """
    GetBlockWithTxsRequest is the request type for the Service.GetBlockWithTxs
    RPC method. Since: cosmos-sdk 0.45.2
    """

    height: int = betterproto.int64_field(1)
    """height is the height of the block to query."""

    pagination: "__base_query_v1_beta1__.PageRequest" = betterproto.message_field(2)
    """pagination defines a pagination for the request."""


@dataclass(eq=False, repr=False)
class GetBlockWithTxsResponse(betterproto.Message):
    """
    GetBlockWithTxsResponse is the response type for the
    Service.GetBlockWithTxs method. Since: cosmos-sdk 0.45.2
    """

    txs: List["Tx"] = betterproto.message_field(1)
    """txs are the transactions in the block."""

    block_id: "___tendermint_types__.BlockId" = betterproto.message_field(2)
    block: "___tendermint_types__.Block" = betterproto.message_field(3)
    pagination: "__base_query_v1_beta1__.PageResponse" = betterproto.message_field(4)
    """pagination defines a pagination for the response."""


@dataclass(eq=False, repr=False)
class TxDecodeRequest(betterproto.Message):
    """
    TxDecodeRequest is the request type for the Service.TxDecode RPC method.
    Since: cosmos-sdk 0.47
    """

    tx_bytes: bytes = betterproto.bytes_field(1)
    """tx_bytes is the raw transaction."""


@dataclass(eq=False, repr=False)
class TxDecodeResponse(betterproto.Message):
    """
    TxDecodeResponse is the response type for the Service.TxDecode method.
    Since: cosmos-sdk 0.47
    """

    tx: "Tx" = betterproto.message_field(1)
    """tx is the decoded transaction."""


@dataclass(eq=False, repr=False)
class TxEncodeRequest(betterproto.Message):
    """
    TxEncodeRequest is the request type for the Service.TxEncode RPC method.
    Since: cosmos-sdk 0.47
    """

    tx: "Tx" = betterproto.message_field(1)
    """tx is the transaction to encode."""


@dataclass(eq=False, repr=False)
class TxEncodeResponse(betterproto.Message):
    """
    TxEncodeResponse is the response type for the Service.TxEncode method.
    Since: cosmos-sdk 0.47
    """

    tx_bytes: bytes = betterproto.bytes_field(1)
    """tx_bytes is the encoded transaction bytes."""


@dataclass(eq=False, repr=False)
class TxEncodeAminoRequest(betterproto.Message):
    """
    TxEncodeAminoRequest is the request type for the Service.TxEncodeAmino RPC
    method. Since: cosmos-sdk 0.47
    """

    amino_json: str = betterproto.string_field(1)


@dataclass(eq=False, repr=False)
class TxEncodeAminoResponse(betterproto.Message):
    """
    TxEncodeAminoResponse is the response type for the Service.TxEncodeAmino
    RPC method. Since: cosmos-sdk 0.47
    """

    amino_binary: bytes = betterproto.bytes_field(1)


@dataclass(eq=False, repr=False)
class TxDecodeAminoRequest(betterproto.Message):
    """
    TxDecodeAminoRequest is the request type for the Service.TxDecodeAmino RPC
    method. Since: cosmos-sdk 0.47
    """

    amino_binary: bytes = betterproto.bytes_field(1)


@dataclass(eq=False, repr=False)
class TxDecodeAminoResponse(betterproto.Message):
    """
    TxDecodeAminoResponse is the response type for the Service.TxDecodeAmino
    RPC method. Since: cosmos-sdk 0.47
    """

    amino_json: str = betterproto.string_field(1)


class ServiceStub(betterproto.ServiceStub):
    async def simulate(
        self,
        simulate_request: "SimulateRequest",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None
    ) -> "SimulateResponse":
        return await self._unary_unary(
            "/cosmos.tx.v1beta1.Service/Simulate",
            simulate_request,
            SimulateResponse,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )

    async def get_tx(
        self,
        get_tx_request: "GetTxRequest",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None
    ) -> "GetTxResponse":
        return await self._unary_unary(
            "/cosmos.tx.v1beta1.Service/GetTx",
            get_tx_request,
            GetTxResponse,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )

    async def broadcast_tx(
        self,
        broadcast_tx_request: "BroadcastTxRequest",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None
    ) -> "BroadcastTxResponse":
        return await self._unary_unary(
            "/cosmos.tx.v1beta1.Service/BroadcastTx",
            broadcast_tx_request,
            BroadcastTxResponse,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )

    async def get_txs_event(
        self,
        get_txs_event_request: "GetTxsEventRequest",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None
    ) -> "GetTxsEventResponse":
        return await self._unary_unary(
            "/cosmos.tx.v1beta1.Service/GetTxsEvent",
            get_txs_event_request,
            GetTxsEventResponse,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )

    async def get_block_with_txs(
        self,
        get_block_with_txs_request: "GetBlockWithTxsRequest",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None
    ) -> "GetBlockWithTxsResponse":
        return await self._unary_unary(
            "/cosmos.tx.v1beta1.Service/GetBlockWithTxs",
            get_block_with_txs_request,
            GetBlockWithTxsResponse,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )

    async def tx_decode(
        self,
        tx_decode_request: "TxDecodeRequest",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None
    ) -> "TxDecodeResponse":
        return await self._unary_unary(
            "/cosmos.tx.v1beta1.Service/TxDecode",
            tx_decode_request,
            TxDecodeResponse,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )

    async def tx_encode(
        self,
        tx_encode_request: "TxEncodeRequest",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None
    ) -> "TxEncodeResponse":
        return await self._unary_unary(
            "/cosmos.tx.v1beta1.Service/TxEncode",
            tx_encode_request,
            TxEncodeResponse,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )

    async def tx_encode_amino(
        self,
        tx_encode_amino_request: "TxEncodeAminoRequest",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None
    ) -> "TxEncodeAminoResponse":
        return await self._unary_unary(
            "/cosmos.tx.v1beta1.Service/TxEncodeAmino",
            tx_encode_amino_request,
            TxEncodeAminoResponse,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )

    async def tx_decode_amino(
        self,
        tx_decode_amino_request: "TxDecodeAminoRequest",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None
    ) -> "TxDecodeAminoResponse":
        return await self._unary_unary(
            "/cosmos.tx.v1beta1.Service/TxDecodeAmino",
            tx_decode_amino_request,
            TxDecodeAminoResponse,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )


class ServiceBase(ServiceBase):
    async def simulate(self, simulate_request: "SimulateRequest") -> "SimulateResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def get_tx(self, get_tx_request: "GetTxRequest") -> "GetTxResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def broadcast_tx(self, broadcast_tx_request: "BroadcastTxRequest") -> "BroadcastTxResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def get_txs_event(self, get_txs_event_request: "GetTxsEventRequest") -> "GetTxsEventResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def get_block_with_txs(
        self, get_block_with_txs_request: "GetBlockWithTxsRequest"
    ) -> "GetBlockWithTxsResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def tx_decode(self, tx_decode_request: "TxDecodeRequest") -> "TxDecodeResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def tx_encode(self, tx_encode_request: "TxEncodeRequest") -> "TxEncodeResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def tx_encode_amino(self, tx_encode_amino_request: "TxEncodeAminoRequest") -> "TxEncodeAminoResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def tx_decode_amino(self, tx_decode_amino_request: "TxDecodeAminoRequest") -> "TxDecodeAminoResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def __rpc_simulate(self, stream: "grpclib.server.Stream[SimulateRequest, SimulateResponse]") -> None:
        request = await stream.recv_message()
        response = await self.simulate(request)
        await stream.send_message(response)

    async def __rpc_get_tx(self, stream: "grpclib.server.Stream[GetTxRequest, GetTxResponse]") -> None:
        request = await stream.recv_message()
        response = await self.get_tx(request)
        await stream.send_message(response)

    async def __rpc_broadcast_tx(
        self, stream: "grpclib.server.Stream[BroadcastTxRequest, BroadcastTxResponse]"
    ) -> None:
        request = await stream.recv_message()
        response = await self.broadcast_tx(request)
        await stream.send_message(response)

    async def __rpc_get_txs_event(
        self, stream: "grpclib.server.Stream[GetTxsEventRequest, GetTxsEventResponse]"
    ) -> None:
        request = await stream.recv_message()
        response = await self.get_txs_event(request)
        await stream.send_message(response)

    async def __rpc_get_block_with_txs(
        self,
        stream: "grpclib.server.Stream[GetBlockWithTxsRequest, GetBlockWithTxsResponse]",
    ) -> None:
        request = await stream.recv_message()
        response = await self.get_block_with_txs(request)
        await stream.send_message(response)

    async def __rpc_tx_decode(self, stream: "grpclib.server.Stream[TxDecodeRequest, TxDecodeResponse]") -> None:
        request = await stream.recv_message()
        response = await self.tx_decode(request)
        await stream.send_message(response)

    async def __rpc_tx_encode(self, stream: "grpclib.server.Stream[TxEncodeRequest, TxEncodeResponse]") -> None:
        request = await stream.recv_message()
        response = await self.tx_encode(request)
        await stream.send_message(response)

    async def __rpc_tx_encode_amino(
        self,
        stream: "grpclib.server.Stream[TxEncodeAminoRequest, TxEncodeAminoResponse]",
    ) -> None:
        request = await stream.recv_message()
        response = await self.tx_encode_amino(request)
        await stream.send_message(response)

    async def __rpc_tx_decode_amino(
        self,
        stream: "grpclib.server.Stream[TxDecodeAminoRequest, TxDecodeAminoResponse]",
    ) -> None:
        request = await stream.recv_message()
        response = await self.tx_decode_amino(request)
        await stream.send_message(response)

    def __mapping__(self) -> Dict[str, grpclib.const.Handler]:
        return {
            "/cosmos.tx.v1beta1.Service/Simulate": grpclib.const.Handler(
                self.__rpc_simulate,
                grpclib.const.Cardinality.UNARY_UNARY,
                SimulateRequest,
                SimulateResponse,
            ),
            "/cosmos.tx.v1beta1.Service/GetTx": grpclib.const.Handler(
                self.__rpc_get_tx,
                grpclib.const.Cardinality.UNARY_UNARY,
                GetTxRequest,
                GetTxResponse,
            ),
            "/cosmos.tx.v1beta1.Service/BroadcastTx": grpclib.const.Handler(
                self.__rpc_broadcast_tx,
                grpclib.const.Cardinality.UNARY_UNARY,
                BroadcastTxRequest,
                BroadcastTxResponse,
            ),
            "/cosmos.tx.v1beta1.Service/GetTxsEvent": grpclib.const.Handler(
                self.__rpc_get_txs_event,
                grpclib.const.Cardinality.UNARY_UNARY,
                GetTxsEventRequest,
                GetTxsEventResponse,
            ),
            "/cosmos.tx.v1beta1.Service/GetBlockWithTxs": grpclib.const.Handler(
                self.__rpc_get_block_with_txs,
                grpclib.const.Cardinality.UNARY_UNARY,
                GetBlockWithTxsRequest,
                GetBlockWithTxsResponse,
            ),
            "/cosmos.tx.v1beta1.Service/TxDecode": grpclib.const.Handler(
                self.__rpc_tx_decode,
                grpclib.const.Cardinality.UNARY_UNARY,
                TxDecodeRequest,
                TxDecodeResponse,
            ),
            "/cosmos.tx.v1beta1.Service/TxEncode": grpclib.const.Handler(
                self.__rpc_tx_encode,
                grpclib.const.Cardinality.UNARY_UNARY,
                TxEncodeRequest,
                TxEncodeResponse,
            ),
            "/cosmos.tx.v1beta1.Service/TxEncodeAmino": grpclib.const.Handler(
                self.__rpc_tx_encode_amino,
                grpclib.const.Cardinality.UNARY_UNARY,
                TxEncodeAminoRequest,
                TxEncodeAminoResponse,
            ),
            "/cosmos.tx.v1beta1.Service/TxDecodeAmino": grpclib.const.Handler(
                self.__rpc_tx_decode_amino,
                grpclib.const.Cardinality.UNARY_UNARY,
                TxDecodeAminoRequest,
                TxDecodeAminoResponse,
            ),
        }


Tx.__pydantic_model__.update_forward_refs()  # type: ignore
SignDocDirectAux.__pydantic_model__.update_forward_refs()  # type: ignore
SignDocEip712.__pydantic_model__.update_forward_refs()  # type: ignore
TxBody.__pydantic_model__.update_forward_refs()  # type: ignore
AuthInfo.__pydantic_model__.update_forward_refs()  # type: ignore
SignerInfo.__pydantic_model__.update_forward_refs()  # type: ignore
ModeInfo.__pydantic_model__.update_forward_refs()  # type: ignore
ModeInfoSingle.__pydantic_model__.update_forward_refs()  # type: ignore
ModeInfoMulti.__pydantic_model__.update_forward_refs()  # type: ignore
Fee.__pydantic_model__.update_forward_refs()  # type: ignore
Tip.__pydantic_model__.update_forward_refs()  # type: ignore
AuxSignerData.__pydantic_model__.update_forward_refs()  # type: ignore
GetTxsEventRequest.__pydantic_model__.update_forward_refs()  # type: ignore
GetTxsEventResponse.__pydantic_model__.update_forward_refs()  # type: ignore
BroadcastTxRequest.__pydantic_model__.update_forward_refs()  # type: ignore
BroadcastTxResponse.__pydantic_model__.update_forward_refs()  # type: ignore
SimulateRequest.__pydantic_model__.update_forward_refs()  # type: ignore
SimulateResponse.__pydantic_model__.update_forward_refs()  # type: ignore
GetTxResponse.__pydantic_model__.update_forward_refs()  # type: ignore
GetBlockWithTxsRequest.__pydantic_model__.update_forward_refs()  # type: ignore
GetBlockWithTxsResponse.__pydantic_model__.update_forward_refs()  # type: ignore
TxDecodeResponse.__pydantic_model__.update_forward_refs()  # type: ignore
TxEncodeRequest.__pydantic_model__.update_forward_refs()  # type: ignore
