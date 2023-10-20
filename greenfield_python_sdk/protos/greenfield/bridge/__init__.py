# Generated by the protocol buffer compiler.  DO NOT EDIT!
# sources: greenfield/bridge/event.proto, greenfield/bridge/genesis.proto, greenfield/bridge/params.proto, greenfield/bridge/query.proto, greenfield/bridge/tx.proto
# plugin: python-betterproto
# This file has been @generated

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dataclasses import dataclass
else:
    from pydantic.dataclasses import dataclass

from typing import TYPE_CHECKING, Dict, Optional

import betterproto
import grpclib
from betterproto.grpc.grpclib_server import ServiceBase

from ...cosmos.base import v1beta1 as __cosmos_base_v1_beta1__

if TYPE_CHECKING:
    import grpclib.server
    from betterproto.grpc.grpclib_client import MetadataLike
    from grpclib.metadata import Deadline


class RefundReason(betterproto.Enum):
    REFUND_REASON_UNKNOWN = 0
    REFUND_REASON_INSUFFICIENT_BALANCE = 1
    REFUND_REASON_FAIL_ACK = 2


@dataclass(eq=False, repr=False)
class EventCrossTransferOut(betterproto.Message):
    """
    EventCrossTransferOut is emitted when a cross chain transfer out tx created
    """

    from_: str = betterproto.string_field(1)
    """From addres of the cross chain transfer tx"""

    to: str = betterproto.string_field(2)
    """To addres of the cross chain transfer tx"""

    amount: "__cosmos_base_v1_beta1__.Coin" = betterproto.message_field(3)
    """Amount of the cross chain transfer tx"""

    relayer_fee: "__cosmos_base_v1_beta1__.Coin" = betterproto.message_field(4)
    """Relayer fee of the cross chain transfer tx"""

    sequence: int = betterproto.uint64_field(5)
    """Sequence of the corresponding cross chain package"""

    dest_chain_id: int = betterproto.uint32_field(6)
    """Destination chain id of the cross chain transfer tx"""


@dataclass(eq=False, repr=False)
class EventCrossTransferOutRefund(betterproto.Message):
    """
    EventCrossTransferOutRefund is emitted when a cross chain transfer out tx
    failed
    """

    refund_address: str = betterproto.string_field(1)
    """Refund address of the failed cross chain transfer tx"""

    amount: "__cosmos_base_v1_beta1__.Coin" = betterproto.message_field(2)
    """Amount of the failed cross chain transfer tx"""

    refund_reason: "RefundReason" = betterproto.enum_field(3)
    """Refund reason of the failed cross chain transfer tx"""

    sequence: int = betterproto.uint64_field(4)
    """Sequence of the corresponding cross chain package"""

    dest_chain_id: int = betterproto.uint32_field(5)
    """Destination chain id of the cross chain transfer tx"""


@dataclass(eq=False, repr=False)
class EventCrossTransferIn(betterproto.Message):
    """
    EventCrossTransferIn is emitted when a cross chain transfer in tx happened
    """

    amount: "__cosmos_base_v1_beta1__.Coin" = betterproto.message_field(1)
    """Amount of the cross chain transfer tx"""

    receiver_address: str = betterproto.string_field(2)
    """Receiver of the cross chain transfer tx"""

    refund_address: str = betterproto.string_field(3)
    """Refund of the cross chain transfer tx in BSC"""

    sequence: int = betterproto.uint64_field(4)
    """Sequence of the corresponding cross chain package"""

    src_chain_id: int = betterproto.uint32_field(5)
    """Source chain id of the cross chain transfer tx"""


@dataclass(eq=False, repr=False)
class Params(betterproto.Message):
    """Params defines the parameters for the module."""

    bsc_transfer_out_relayer_fee: str = betterproto.string_field(1)
    """Relayer fee for the cross chain transfer out tx to bsc"""

    bsc_transfer_out_ack_relayer_fee: str = betterproto.string_field(2)
    """
    Relayer fee for the ACK or FAIL_ACK package of the cross chain transfer out
    tx to bsc
    """


@dataclass(eq=False, repr=False)
class GenesisState(betterproto.Message):
    """GenesisState defines the bridge module's genesis state."""

    params: "Params" = betterproto.message_field(1)
    """Params defines all the paramaters of the module."""


@dataclass(eq=False, repr=False)
class QueryParamsRequest(betterproto.Message):
    """QueryParamsRequest is request type for the Query/Params RPC method."""

    pass


@dataclass(eq=False, repr=False)
class QueryParamsResponse(betterproto.Message):
    """
    QueryParamsResponse is response type for the Query/Params RPC method.
    """

    params: "Params" = betterproto.message_field(1)
    """params holds all the parameters of this module."""


@dataclass(eq=False, repr=False)
class MsgTransferOut(betterproto.Message):
    """MsgTransferOut is the Msg/TransferOut request type."""

    from_: str = betterproto.string_field(1)
    """from address"""

    to: str = betterproto.string_field(2)
    """to address"""

    amount: "__cosmos_base_v1_beta1__.Coin" = betterproto.message_field(3)
    """transfer token amount"""


@dataclass(eq=False, repr=False)
class MsgTransferOutResponse(betterproto.Message):
    """MsgTransferOutResponse is the Msg/TransferOut response type."""

    pass


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
    params defines the x/crosschain parameters to update. NOTE: All parameters
    must be supplied.
    """


@dataclass(eq=False, repr=False)
class MsgUpdateParamsResponse(betterproto.Message):
    """
    MsgUpdateParamsResponse defines the response structure for executing a
    MsgUpdateParams message.
    """

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
            "/greenfield.bridge.Query/Params",
            query_params_request,
            QueryParamsResponse,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )


class MsgStub(betterproto.ServiceStub):
    async def transfer_out(
        self,
        msg_transfer_out: "MsgTransferOut",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None
    ) -> "MsgTransferOutResponse":
        return await self._unary_unary(
            "/greenfield.bridge.Msg/TransferOut",
            msg_transfer_out,
            MsgTransferOutResponse,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )

    async def update_params(
        self,
        msg_update_params: "MsgUpdateParams",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None
    ) -> "MsgUpdateParamsResponse":
        return await self._unary_unary(
            "/greenfield.bridge.Msg/UpdateParams",
            msg_update_params,
            MsgUpdateParamsResponse,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )


class QueryBase(ServiceBase):
    async def params(self, query_params_request: "QueryParamsRequest") -> "QueryParamsResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def __rpc_params(self, stream: "grpclib.server.Stream[QueryParamsRequest, QueryParamsResponse]") -> None:
        request = await stream.recv_message()
        response = await self.params(request)
        await stream.send_message(response)

    def __mapping__(self) -> Dict[str, grpclib.const.Handler]:
        return {
            "/greenfield.bridge.Query/Params": grpclib.const.Handler(
                self.__rpc_params,
                grpclib.const.Cardinality.UNARY_UNARY,
                QueryParamsRequest,
                QueryParamsResponse,
            ),
        }


class MsgBase(ServiceBase):
    async def transfer_out(self, msg_transfer_out: "MsgTransferOut") -> "MsgTransferOutResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def update_params(self, msg_update_params: "MsgUpdateParams") -> "MsgUpdateParamsResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def __rpc_transfer_out(self, stream: "grpclib.server.Stream[MsgTransferOut, MsgTransferOutResponse]") -> None:
        request = await stream.recv_message()
        response = await self.transfer_out(request)
        await stream.send_message(response)

    async def __rpc_update_params(
        self, stream: "grpclib.server.Stream[MsgUpdateParams, MsgUpdateParamsResponse]"
    ) -> None:
        request = await stream.recv_message()
        response = await self.update_params(request)
        await stream.send_message(response)

    def __mapping__(self) -> Dict[str, grpclib.const.Handler]:
        return {
            "/greenfield.bridge.Msg/TransferOut": grpclib.const.Handler(
                self.__rpc_transfer_out,
                grpclib.const.Cardinality.UNARY_UNARY,
                MsgTransferOut,
                MsgTransferOutResponse,
            ),
            "/greenfield.bridge.Msg/UpdateParams": grpclib.const.Handler(
                self.__rpc_update_params,
                grpclib.const.Cardinality.UNARY_UNARY,
                MsgUpdateParams,
                MsgUpdateParamsResponse,
            ),
        }


EventCrossTransferOut.__pydantic_model__.update_forward_refs()  # type: ignore
EventCrossTransferOutRefund.__pydantic_model__.update_forward_refs()  # type: ignore
EventCrossTransferIn.__pydantic_model__.update_forward_refs()  # type: ignore
GenesisState.__pydantic_model__.update_forward_refs()  # type: ignore
QueryParamsResponse.__pydantic_model__.update_forward_refs()  # type: ignore
MsgTransferOut.__pydantic_model__.update_forward_refs()  # type: ignore
MsgUpdateParams.__pydantic_model__.update_forward_refs()  # type: ignore
