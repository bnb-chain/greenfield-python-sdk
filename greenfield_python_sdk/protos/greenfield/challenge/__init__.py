# Generated by the protocol buffer compiler.  DO NOT EDIT!
# sources: greenfield/challenge/events.proto, greenfield/challenge/genesis.proto, greenfield/challenge/params.proto, greenfield/challenge/query.proto, greenfield/challenge/tx.proto, greenfield/challenge/types.proto
# plugin: python-betterproto
# This file has been @generated
from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict, List, Optional

import betterproto
import grpclib
from betterproto.grpc.grpclib_server import ServiceBase

if TYPE_CHECKING:
    import grpclib.server
    from betterproto.grpc.grpclib_client import MetadataLike
    from grpclib.metadata import Deadline


class VoteResult(betterproto.Enum):
    """VoteResult defines the result attestation for a challenge."""

    CHALLENGE_FAILED = 0
    """The challenge failed."""

    CHALLENGE_SUCCEED = 1
    """The challenge succeed."""


@dataclass(eq=False, repr=False)
class Slash(betterproto.Message):
    """
    Slash records the storage provider slashes, which will be pruned periodically.
    """

    sp_id: int = betterproto.uint32_field(1)
    """The slashed storage provider."""

    object_id: str = betterproto.string_field(2)
    """The slashed object info."""

    height: int = betterproto.uint64_field(3)
    """The height when the slash happened, which is used for prune purpose."""


@dataclass(eq=False, repr=False)
class Challenge(betterproto.Message):
    """Challenge records the challenge which are not expired yet."""

    id: int = betterproto.uint64_field(1)
    """The id of the challenge."""

    expired_height: int = betterproto.uint64_field(2)
    """The height at which the challenge will be expired."""


@dataclass(eq=False, repr=False)
class AttestedChallenge(betterproto.Message):
    """AttestedChallenge records the challenge which are attested."""

    id: int = betterproto.uint64_field(1)
    """The id of the challenge."""

    result: "VoteResult" = betterproto.enum_field(2)
    """The attestation result of the challenge."""


@dataclass(eq=False, repr=False)
class AttestedChallengeIds(betterproto.Message):
    """
    AttestedChallengeIds stored fixed number of the latest attested challenge ids.
    To use the storage more efficiently, a circular queue will be constructed using
    these fields.
    """

    size: int = betterproto.uint64_field(1)
    """The fixed number of challenge ids to save."""

    challenges: List["AttestedChallenge"] = betterproto.message_field(2)
    """The latest attested challenges."""

    cursor: int = betterproto.int64_field(3)
    """The cursor to retrieve data from the ids field."""


@dataclass(eq=False, repr=False)
class EventStartChallenge(betterproto.Message):
    """EventStartChallenge to indicate a challenge has bee created."""

    challenge_id: int = betterproto.uint64_field(1)
    """The id of challenge, which is generated by blockchain."""

    object_id: str = betterproto.string_field(2)
    """The id of object info to be challenged."""

    segment_index: int = betterproto.uint32_field(3)
    """The segment/piece index of the object info."""

    sp_id: int = betterproto.uint32_field(4)
    """The storage provider to be challenged."""

    sp_operator_address: str = betterproto.string_field(5)
    """The storage provider to be challenged."""

    redundancy_index: int = betterproto.int32_field(6)
    """The redundancy index, which comes from the index of storage providers."""

    challenger_address: str = betterproto.string_field(7)
    """The challenger who submits the challenge."""

    expired_height: int = betterproto.uint64_field(8)
    """The challenge will be expired after this height"""


@dataclass(eq=False, repr=False)
class EventAttestChallenge(betterproto.Message):
    """EventAttestChallenge to indicate a challenge has been attested."""

    challenge_id: int = betterproto.uint64_field(1)
    """The id of challenge."""

    result: "VoteResult" = betterproto.enum_field(2)
    """The result of challenge."""

    sp_id: int = betterproto.uint32_field(3)
    """The slashed storage provider address."""

    slash_amount: str = betterproto.string_field(4)
    """The slashed amount from the storage provider."""

    challenger_address: str = betterproto.string_field(5)
    """The address of challenger."""

    challenger_reward_amount: str = betterproto.string_field(6)
    """The reward amount to the challenger."""

    submitter_address: str = betterproto.string_field(7)
    """The submitter of the challenge attestation."""

    submitter_reward_amount: str = betterproto.string_field(8)
    """The reward amount to the submitter."""

    validator_reward_amount: str = betterproto.string_field(10)
    """The reward amount to all current validators."""


@dataclass(eq=False, repr=False)
class Params(betterproto.Message):
    """Params defines the parameters for the module."""

    challenge_count_per_block: int = betterproto.uint64_field(1)
    """
    Challenges which will be emitted in each block, including user submitted or randomly
    triggered.
    """

    challenge_keep_alive_period: int = betterproto.uint64_field(2)
    """
    Challenges will be expired after the period, including user submitted or randomly
    triggered.
    """

    slash_cooling_off_period: int = betterproto.uint64_field(3)
    """
    The count of blocks to stand for the period in which the same storage and object
    info cannot be slashed again.
    """

    slash_amount_size_rate: str = betterproto.string_field(4)
    """
    The slash coin amount will be calculated from the size of object info, and adjusted
    by this rate.
    """

    slash_amount_min: str = betterproto.string_field(5)
    """The minimal slash amount."""

    slash_amount_max: str = betterproto.string_field(6)
    """The maximum slash amount."""

    reward_validator_ratio: str = betterproto.string_field(7)
    """The ratio of slash amount to reward all current validators."""

    reward_submitter_ratio: str = betterproto.string_field(8)
    """The ratio of reward amount to reward attestation submitter."""

    reward_submitter_threshold: str = betterproto.string_field(9)
    """The reward amount to submitter will be adjusted by the threshold."""

    heartbeat_interval: int = betterproto.uint64_field(10)
    """
    Heartbeat interval, based on challenge id, defines the frequency of heartbeat
    attestation.
    """

    attestation_inturn_interval: int = betterproto.uint64_field(11)
    """The time duration for each submitter to submit attestations in turn."""

    attestation_kept_count: int = betterproto.uint64_field(12)
    """The number of kept attested challenge ids, which can be queried by clients."""

    sp_slash_max_amount: str = betterproto.string_field(13)
    """The max slash amount for a sp in a counting window."""

    sp_slash_counting_window: int = betterproto.uint64_field(14)
    """The number of blocks to count how much a sp had been slashed."""


@dataclass(eq=False, repr=False)
class GenesisState(betterproto.Message):
    """GenesisState defines the challenge module's genesis state."""

    params: "Params" = betterproto.message_field(1)


@dataclass(eq=False, repr=False)
class QueryParamsRequest(betterproto.Message):
    """QueryParamsRequest is request type for the Query/Params RPC method."""

    pass


@dataclass(eq=False, repr=False)
class QueryParamsResponse(betterproto.Message):
    """QueryParamsResponse is response type for the Query/Params RPC method."""

    params: "Params" = betterproto.message_field(1)
    """params holds all the parameters of this module."""


@dataclass(eq=False, repr=False)
class QueryAttestedChallengeRequest(betterproto.Message):
    """
    QueryAttestedChallengeRequest is request type for the Query/AttestedChallenge RPC
    method.
    """

    challenge_id: int = betterproto.uint64_field(1)
    """The id of the challenge."""


@dataclass(eq=False, repr=False)
class QueryAttestedChallengeResponse(betterproto.Message):
    """
    QueryAttestedChallengeResponse is response type for the Query/AttestedChallenge RPC
    method.
    """

    challenge: "AttestedChallenge" = betterproto.message_field(1)


@dataclass(eq=False, repr=False)
class QueryLatestAttestedChallengesRequest(betterproto.Message):
    """
    QueryLatestAttestedChallengesRequest is request type for the
    Query/LatestAttestedChallenges RPC method.
    """

    pass


@dataclass(eq=False, repr=False)
class QueryLatestAttestedChallengesResponse(betterproto.Message):
    """
    QueryLatestAttestedChallengesResponse is response type for the
    Query/LatestAttestedChallenges RPC method.
    """

    challenges: List["AttestedChallenge"] = betterproto.message_field(1)


@dataclass(eq=False, repr=False)
class QueryInturnAttestationSubmitterRequest(betterproto.Message):
    """
    QueryInturnAttestationSubmitterRequest is request type for the
    Query/InturnAttestationSubmitter RPC method.
    """

    pass


@dataclass(eq=False, repr=False)
class QueryInturnAttestationSubmitterResponse(betterproto.Message):
    """
    QueryInturnAttestationSubmitterResponse is response type for the
    Query/InturnAttestationSubmitter RPC method.
    """

    bls_pub_key: str = betterproto.string_field(1)
    submit_interval: "SubmitInterval" = betterproto.message_field(2)


@dataclass(eq=False, repr=False)
class SubmitInterval(betterproto.Message):
    """
    SubmitInterval holds start and end (exclusive) (i.e., [start, end)) time of in turn
    attestation.
    """

    start: int = betterproto.uint64_field(1)
    end: int = betterproto.uint64_field(2)


@dataclass(eq=False, repr=False)
class MsgSubmit(betterproto.Message):
    """MsgSubmit defines the message for submitting challenges."""

    challenger: str = betterproto.string_field(1)
    """The challenger address."""

    sp_operator_address: str = betterproto.string_field(2)
    """The storage provider to be challenged."""

    bucket_name: str = betterproto.string_field(3)
    """The bucket of the object info to be challenged."""

    object_name: str = betterproto.string_field(4)
    """The name of the object info to be challenged."""

    segment_index: int = betterproto.uint32_field(5)
    """The index of segment/piece to challenge, start from zero."""

    random_index: bool = betterproto.bool_field(6)
    """Randomly pick a segment/piece to challenge or not."""


@dataclass(eq=False, repr=False)
class MsgSubmitResponse(betterproto.Message):
    """MsgSubmitResponse defines the response of MsgSubmit."""

    challenge_id: int = betterproto.uint64_field(1)
    """The id of the challenge."""


@dataclass(eq=False, repr=False)
class MsgAttest(betterproto.Message):
    """MsgSubmit defines the message for attesting challenges."""

    submitter: str = betterproto.string_field(1)
    """The submitter address."""

    challenge_id: int = betterproto.uint64_field(2)
    """The id of the challenge."""

    object_id: str = betterproto.string_field(3)
    """The id of the object info."""

    sp_operator_address: str = betterproto.string_field(4)
    """The storage provider to be challenged."""

    vote_result: "VoteResult" = betterproto.enum_field(5)
    """Vote result of the attestation."""

    challenger_address: str = betterproto.string_field(6)
    """The challenger who submits the challenge, which can be empty."""

    vote_validator_set: List[int] = betterproto.fixed64_field(7)
    """The validators participated in the attestation."""

    vote_agg_signature: bytes = betterproto.bytes_field(8)
    """The aggregated BLS signature from the validators."""


@dataclass(eq=False, repr=False)
class MsgAttestResponse(betterproto.Message):
    """MsgAttest defines the response of MsgAttestResponse."""

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
    params defines the x/challenge parameters to update.
    NOTE: All parameters must be supplied.
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
            "/greenfield.challenge.Query/Params",
            query_params_request,
            QueryParamsResponse,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )

    async def attested_challenge(
        self,
        query_attested_challenge_request: "QueryAttestedChallengeRequest",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None
    ) -> "QueryAttestedChallengeResponse":
        return await self._unary_unary(
            "/greenfield.challenge.Query/AttestedChallenge",
            query_attested_challenge_request,
            QueryAttestedChallengeResponse,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )

    async def latest_attested_challenges(
        self,
        query_latest_attested_challenges_request: "QueryLatestAttestedChallengesRequest",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None
    ) -> "QueryLatestAttestedChallengesResponse":
        return await self._unary_unary(
            "/greenfield.challenge.Query/LatestAttestedChallenges",
            query_latest_attested_challenges_request,
            QueryLatestAttestedChallengesResponse,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )

    async def inturn_attestation_submitter(
        self,
        query_inturn_attestation_submitter_request: "QueryInturnAttestationSubmitterRequest",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None
    ) -> "QueryInturnAttestationSubmitterResponse":
        return await self._unary_unary(
            "/greenfield.challenge.Query/InturnAttestationSubmitter",
            query_inturn_attestation_submitter_request,
            QueryInturnAttestationSubmitterResponse,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )


class MsgStub(betterproto.ServiceStub):
    async def submit(
        self,
        msg_submit: "MsgSubmit",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None
    ) -> "MsgSubmitResponse":
        return await self._unary_unary(
            "/greenfield.challenge.Msg/Submit",
            msg_submit,
            MsgSubmitResponse,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )

    async def attest(
        self,
        msg_attest: "MsgAttest",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None
    ) -> "MsgAttestResponse":
        return await self._unary_unary(
            "/greenfield.challenge.Msg/Attest",
            msg_attest,
            MsgAttestResponse,
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
            "/greenfield.challenge.Msg/UpdateParams",
            msg_update_params,
            MsgUpdateParamsResponse,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )


class QueryBase(ServiceBase):
    async def params(self, query_params_request: "QueryParamsRequest") -> "QueryParamsResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def attested_challenge(
        self, query_attested_challenge_request: "QueryAttestedChallengeRequest"
    ) -> "QueryAttestedChallengeResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def latest_attested_challenges(
        self,
        query_latest_attested_challenges_request: "QueryLatestAttestedChallengesRequest",
    ) -> "QueryLatestAttestedChallengesResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def inturn_attestation_submitter(
        self,
        query_inturn_attestation_submitter_request: "QueryInturnAttestationSubmitterRequest",
    ) -> "QueryInturnAttestationSubmitterResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def __rpc_params(self, stream: "grpclib.server.Stream[QueryParamsRequest, QueryParamsResponse]") -> None:
        request = await stream.recv_message()
        response = await self.params(request)
        await stream.send_message(response)

    async def __rpc_attested_challenge(
        self,
        stream: "grpclib.server.Stream[QueryAttestedChallengeRequest, QueryAttestedChallengeResponse]",
    ) -> None:
        request = await stream.recv_message()
        response = await self.attested_challenge(request)
        await stream.send_message(response)

    async def __rpc_latest_attested_challenges(
        self,
        stream: "grpclib.server.Stream[QueryLatestAttestedChallengesRequest, QueryLatestAttestedChallengesResponse]",
    ) -> None:
        request = await stream.recv_message()
        response = await self.latest_attested_challenges(request)
        await stream.send_message(response)

    async def __rpc_inturn_attestation_submitter(
        self,
        stream: "grpclib.server.Stream[QueryInturnAttestationSubmitterRequest, QueryInturnAttestationSubmitterResponse]",
    ) -> None:
        request = await stream.recv_message()
        response = await self.inturn_attestation_submitter(request)
        await stream.send_message(response)

    def __mapping__(self) -> Dict[str, grpclib.const.Handler]:
        return {
            "/greenfield.challenge.Query/Params": grpclib.const.Handler(
                self.__rpc_params,
                grpclib.const.Cardinality.UNARY_UNARY,
                QueryParamsRequest,
                QueryParamsResponse,
            ),
            "/greenfield.challenge.Query/AttestedChallenge": grpclib.const.Handler(
                self.__rpc_attested_challenge,
                grpclib.const.Cardinality.UNARY_UNARY,
                QueryAttestedChallengeRequest,
                QueryAttestedChallengeResponse,
            ),
            "/greenfield.challenge.Query/LatestAttestedChallenges": grpclib.const.Handler(
                self.__rpc_latest_attested_challenges,
                grpclib.const.Cardinality.UNARY_UNARY,
                QueryLatestAttestedChallengesRequest,
                QueryLatestAttestedChallengesResponse,
            ),
            "/greenfield.challenge.Query/InturnAttestationSubmitter": grpclib.const.Handler(
                self.__rpc_inturn_attestation_submitter,
                grpclib.const.Cardinality.UNARY_UNARY,
                QueryInturnAttestationSubmitterRequest,
                QueryInturnAttestationSubmitterResponse,
            ),
        }


class MsgBase(ServiceBase):
    async def submit(self, msg_submit: "MsgSubmit") -> "MsgSubmitResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def attest(self, msg_attest: "MsgAttest") -> "MsgAttestResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def update_params(self, msg_update_params: "MsgUpdateParams") -> "MsgUpdateParamsResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def __rpc_submit(self, stream: "grpclib.server.Stream[MsgSubmit, MsgSubmitResponse]") -> None:
        request = await stream.recv_message()
        response = await self.submit(request)
        await stream.send_message(response)

    async def __rpc_attest(self, stream: "grpclib.server.Stream[MsgAttest, MsgAttestResponse]") -> None:
        request = await stream.recv_message()
        response = await self.attest(request)
        await stream.send_message(response)

    async def __rpc_update_params(
        self, stream: "grpclib.server.Stream[MsgUpdateParams, MsgUpdateParamsResponse]"
    ) -> None:
        request = await stream.recv_message()
        response = await self.update_params(request)
        await stream.send_message(response)

    def __mapping__(self) -> Dict[str, grpclib.const.Handler]:
        return {
            "/greenfield.challenge.Msg/Submit": grpclib.const.Handler(
                self.__rpc_submit,
                grpclib.const.Cardinality.UNARY_UNARY,
                MsgSubmit,
                MsgSubmitResponse,
            ),
            "/greenfield.challenge.Msg/Attest": grpclib.const.Handler(
                self.__rpc_attest,
                grpclib.const.Cardinality.UNARY_UNARY,
                MsgAttest,
                MsgAttestResponse,
            ),
            "/greenfield.challenge.Msg/UpdateParams": grpclib.const.Handler(
                self.__rpc_update_params,
                grpclib.const.Cardinality.UNARY_UNARY,
                MsgUpdateParams,
                MsgUpdateParamsResponse,
            ),
        }
