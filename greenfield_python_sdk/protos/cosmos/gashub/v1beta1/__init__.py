# Generated by the protocol buffer compiler.  DO NOT EDIT!
# sources: cosmos/gashub/v1beta1/event.proto, cosmos/gashub/v1beta1/gashub.proto, cosmos/gashub/v1beta1/genesis.proto, cosmos/gashub/v1beta1/query.proto, cosmos/gashub/v1beta1/tx.proto
# plugin: python-betterproto
# This file has been @generated
from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict, List, Optional

import betterproto
import grpclib
from betterproto.grpc.grpclib_server import ServiceBase

from ...base.query import v1beta1 as __base_query_v1_beta1__

if TYPE_CHECKING:
    import grpclib.server
    from betterproto.grpc.grpclib_client import MetadataLike
    from grpclib.metadata import Deadline


@dataclass(eq=False, repr=False)
class EventUpdateMsgGasParams(betterproto.Message):
    """EventUpdateMsgGasParams is emitted when updating a message's gas params"""

    msg_type_url: str = betterproto.string_field(1)
    """msg_type_url is the type url of the message"""

    from_value: str = betterproto.string_field(2)
    """from_value is the previous gas params"""

    to_value: str = betterproto.string_field(3)
    """to_value is the new gas params"""


@dataclass(eq=False, repr=False)
class Params(betterproto.Message):
    """Params defines the parameters for the gashub module."""

    max_tx_size: int = betterproto.uint64_field(1)
    """max_tx_size is the maximum size of a transaction's bytes."""

    min_gas_per_byte: int = betterproto.uint64_field(2)
    """min_gas_per_byte is the minimum gas to be paid per byte of a transaction's"""


@dataclass(eq=False, repr=False)
class MsgGasParams(betterproto.Message):
    """MsgGasParams defines gas consumption for a msg type"""

    msg_type_url: str = betterproto.string_field(1)
    fixed_type: "MsgGasParamsFixedGasParams" = betterproto.message_field(2, group="gas_params")
    """fixed_type specifies fixed type gas params."""

    grant_type: "MsgGasParamsDynamicGasParams" = betterproto.message_field(3, group="gas_params")
    """grant_type specifies dynamic type gas params for msg/grant."""

    multi_send_type: "MsgGasParamsDynamicGasParams" = betterproto.message_field(4, group="gas_params")
    """grant_type specifies dynamic type gas params for msg/multiSend."""

    grant_allowance_type: "MsgGasParamsDynamicGasParams" = betterproto.message_field(5, group="gas_params")
    """grant_type specifies dynamic type gas params for msg/grantAllowance."""


@dataclass(eq=False, repr=False)
class MsgGasParamsFixedGasParams(betterproto.Message):
    """FixedGasParams defines the parameters for fixed gas type."""

    fixed_gas: int = betterproto.uint64_field(1)
    """fixed_gas is the gas cost for a fixed type msg"""


@dataclass(eq=False, repr=False)
class MsgGasParamsDynamicGasParams(betterproto.Message):
    """DynamicGasParams defines the parameters for dynamic gas type."""

    fixed_gas: int = betterproto.uint64_field(1)
    """fixed_gas is the base gas cost for a dynamic type msg"""

    gas_per_item: int = betterproto.uint64_field(2)
    """gas_per_item is the gas cost for a dynamic type msg per item"""


@dataclass(eq=False, repr=False)
class GenesisState(betterproto.Message):
    """GenesisState defines the gashub module's genesis state."""

    params: "Params" = betterproto.message_field(1)
    """params defines all the parameters of the module."""

    msg_gas_params: List["MsgGasParams"] = betterproto.message_field(2)
    """msg_gas_params defines the gas consumption for a msg type."""


@dataclass(eq=False, repr=False)
class QueryParamsRequest(betterproto.Message):
    """QueryParamsRequest defines the request type for querying x/gashub parameters."""

    pass


@dataclass(eq=False, repr=False)
class QueryParamsResponse(betterproto.Message):
    """
    QueryParamsResponse defines the response type for querying x/gashub parameters.
    """

    params: "Params" = betterproto.message_field(1)


@dataclass(eq=False, repr=False)
class QueryMsgGasParamsRequest(betterproto.Message):
    """
    QueryMsgGasParamsRequest defines the RPC request for looking up MsgGasParams
    entries.
    """

    msg_type_urls: List[str] = betterproto.string_field(1)
    """
    msg_type_urls is the specific type urls you want look up. Leave empty to get all
    entries.
    """

    pagination: "__base_query_v1_beta1__.PageRequest" = betterproto.message_field(99)
    """
    pagination defines an optional pagination for the request. This field is
    only read if the msg_type_urls field is empty.
    """


@dataclass(eq=False, repr=False)
class QueryMsgGasParamsResponse(betterproto.Message):
    """QueryMsgGasParamsResponse defines the RPC response of a MsgGasParams query."""

    msg_gas_params: List["MsgGasParams"] = betterproto.message_field(1)
    pagination: "__base_query_v1_beta1__.PageResponse" = betterproto.message_field(99)
    """
    pagination defines the pagination in the response. This field is only
    populated if the msg_type_urls field in the request is empty.
    """


@dataclass(eq=False, repr=False)
class MsgUpdateParams(betterproto.Message):
    """MsgUpdateParams is the Msg/UpdateParams request type."""

    authority: str = betterproto.string_field(1)
    """
    authority is the address that controls the module (defaults to x/gov unless
    overwritten).
    """

    params: "Params" = betterproto.message_field(2)
    """
    params defines the x/gashub parameters to update.
    NOTE: All parameters must be supplied.
    """


@dataclass(eq=False, repr=False)
class MsgUpdateParamsResponse(betterproto.Message):
    """
    MsgUpdateParamsResponse defines the response structure for executing a
    MsgUpdateParams message.
    """

    pass


@dataclass(eq=False, repr=False)
class MsgSetMsgGasParams(betterproto.Message):
    """
    MsgSetMsgGasParams is the Msg/SetMsgGasParams request type.
    Only entries to add/update/delete need to be included.
    Existing MsgGasParams entries that are not included in this
    message are left unchanged.
    """

    authority: str = betterproto.string_field(1)
    update_set: List["MsgGasParams"] = betterproto.message_field(2)
    """update_set is the list of entries to add or update."""

    delete_set: List[str] = betterproto.string_field(3)
    """
    delete_set is a list of msg types that will have their MsgGasParams entries deleted.
    If a msg type is included that doesn't have a MsgGasParams entry,
    it will be ignored.
    """


@dataclass(eq=False, repr=False)
class MsgSetMsgGasParamsResponse(betterproto.Message):
    """MsgSetMsgGasParamsResponse defines the Msg/SetMsgGasParams response type."""

    pass


class QueryStub(betterproto.ServiceStub):
    async def params(
        self,
        query_params_request: "QueryParamsRequest",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None
    ) -> "QueryParamsResponse":
        return await self._unary_unary(
            "/cosmos.gashub.v1beta1.Query/Params",
            query_params_request,
            QueryParamsResponse,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )

    async def msg_gas_params(
        self,
        query_msg_gas_params_request: "QueryMsgGasParamsRequest",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None
    ) -> "QueryMsgGasParamsResponse":
        return await self._unary_unary(
            "/cosmos.gashub.v1beta1.Query/MsgGasParams",
            query_msg_gas_params_request,
            QueryMsgGasParamsResponse,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )


class MsgStub(betterproto.ServiceStub):
    async def update_params(
        self,
        msg_update_params: "MsgUpdateParams",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None
    ) -> "MsgUpdateParamsResponse":
        return await self._unary_unary(
            "/cosmos.gashub.v1beta1.Msg/UpdateParams",
            msg_update_params,
            MsgUpdateParamsResponse,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )

    async def set_msg_gas_params(
        self,
        msg_set_msg_gas_params: "MsgSetMsgGasParams",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None
    ) -> "MsgSetMsgGasParamsResponse":
        return await self._unary_unary(
            "/cosmos.gashub.v1beta1.Msg/SetMsgGasParams",
            msg_set_msg_gas_params,
            MsgSetMsgGasParamsResponse,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )


class QueryBase(ServiceBase):
    async def params(self, query_params_request: "QueryParamsRequest") -> "QueryParamsResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def msg_gas_params(
        self, query_msg_gas_params_request: "QueryMsgGasParamsRequest"
    ) -> "QueryMsgGasParamsResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def __rpc_params(self, stream: "grpclib.server.Stream[QueryParamsRequest, QueryParamsResponse]") -> None:
        request = await stream.recv_message()
        response = await self.params(request)
        await stream.send_message(response)

    async def __rpc_msg_gas_params(
        self,
        stream: "grpclib.server.Stream[QueryMsgGasParamsRequest, QueryMsgGasParamsResponse]",
    ) -> None:
        request = await stream.recv_message()
        response = await self.msg_gas_params(request)
        await stream.send_message(response)

    def __mapping__(self) -> Dict[str, grpclib.const.Handler]:
        return {
            "/cosmos.gashub.v1beta1.Query/Params": grpclib.const.Handler(
                self.__rpc_params,
                grpclib.const.Cardinality.UNARY_UNARY,
                QueryParamsRequest,
                QueryParamsResponse,
            ),
            "/cosmos.gashub.v1beta1.Query/MsgGasParams": grpclib.const.Handler(
                self.__rpc_msg_gas_params,
                grpclib.const.Cardinality.UNARY_UNARY,
                QueryMsgGasParamsRequest,
                QueryMsgGasParamsResponse,
            ),
        }


class MsgBase(ServiceBase):
    async def update_params(self, msg_update_params: "MsgUpdateParams") -> "MsgUpdateParamsResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def set_msg_gas_params(self, msg_set_msg_gas_params: "MsgSetMsgGasParams") -> "MsgSetMsgGasParamsResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def __rpc_update_params(
        self, stream: "grpclib.server.Stream[MsgUpdateParams, MsgUpdateParamsResponse]"
    ) -> None:
        request = await stream.recv_message()
        response = await self.update_params(request)
        await stream.send_message(response)

    async def __rpc_set_msg_gas_params(
        self,
        stream: "grpclib.server.Stream[MsgSetMsgGasParams, MsgSetMsgGasParamsResponse]",
    ) -> None:
        request = await stream.recv_message()
        response = await self.set_msg_gas_params(request)
        await stream.send_message(response)

    def __mapping__(self) -> Dict[str, grpclib.const.Handler]:
        return {
            "/cosmos.gashub.v1beta1.Msg/UpdateParams": grpclib.const.Handler(
                self.__rpc_update_params,
                grpclib.const.Cardinality.UNARY_UNARY,
                MsgUpdateParams,
                MsgUpdateParamsResponse,
            ),
            "/cosmos.gashub.v1beta1.Msg/SetMsgGasParams": grpclib.const.Handler(
                self.__rpc_set_msg_gas_params,
                grpclib.const.Cardinality.UNARY_UNARY,
                MsgSetMsgGasParams,
                MsgSetMsgGasParamsResponse,
            ),
        }
