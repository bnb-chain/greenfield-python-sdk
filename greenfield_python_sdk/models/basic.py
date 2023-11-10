from typing import List, Optional

import betterproto.lib.google.protobuf as betterproto_lib_google_protobuf
from pydantic import BaseModel

from greenfield_python_sdk.protos.cosmos.base.tendermint.v1beta1 import Validator
from greenfield_python_sdk.protos.tendermint import crypto as _crypto__
from greenfield_python_sdk.protos.tendermint import version as _version__
from greenfield_python_sdk.protos.tendermint.abci import Event, EventAttribute, ResponseDeliverTx, ValidatorUpdate
from greenfield_python_sdk.protos.tendermint.p2p import DefaultNodeInfo, DefaultNodeInfoOther
from greenfield_python_sdk.protos.tendermint.types import (
    BlockParams,
    CommitSig,
    ConsensusParams,
    EvidenceParams,
    SignedHeader,
    ValidatorParams,
    VersionParams,
)


class ResultBlockResults(BaseModel):
    height: int
    txs_results: Optional[List[ResponseDeliverTx]]
    begin_block_events: Optional[List[Event]]
    begin_block_extra_data: bytes
    end_block_events: Optional[List[Event]]
    end_block_extra_data: bytes
    validator_updates: Optional[List[ValidatorUpdate]]
    consensus_param_updates: ConsensusParams


class SyncInfo(BaseModel):
    latest_block_hash: str
    latest_app_hash: str
    latest_block_height: str
    latest_block_time: str
    earliest_block_hash: str
    earliest_app_hash: str
    earliest_block_height: str
    earliest_block_time: str
    catching_up: bool


class ResultStatus(BaseModel):
    node_info: DefaultNodeInfo
    sync_info: SyncInfo
    validator_info: Validator


class ResultCommit(BaseModel):
    signed_header: SignedHeader
