from dataclasses import dataclass
from typing import List, Optional

import betterproto
from pydantic import BaseModel

from greenfield_python_sdk.protos.cosmos.base.v1beta1 import Coin
from greenfield_python_sdk.protos.cosmos.tx.v1beta1 import BroadcastMode, Tip


class SignModeData(betterproto.Enum):
    """
    SIGN_MODE_UNSPECIFIED specifies an unknown signing mode and will be
        rejected.
    """

    SignMode_SIGN_MODE_UNSPECIFIED = 0
    """
    SIGN_MODE_DIRECT specifies a signing mode which uses SignDoc and is
	verified with raw bytes from Tx.
    """
    SignMode_SIGN_MODE_DIRECT = 1
    """
    SIGN_MODE_TEXTUAL is a future signing mode that will verify some
	human-readable textual representation on top of the binary representation
	from SIGN_MODE_DIRECT. It is currently not supported.
    """

    SignMode_SIGN_MODE_TEXTUAL = 2
    """
    SIGN_MODE_DIRECT_AUX specifies a signing mode which uses
	SignDocDirectAux. As opposed to SIGN_MODE_DIRECT, this sign mode does not
	require signers signing over other signers' `signer_info`. It also allows
	for adding Tips in transactions.
	
	Since: cosmos-sdk 0.46
    """
    SignMode_SIGN_MODE_DIRECT_AUX = 3
    """
    SIGN_MODE_LEGACY_AMINO_JSON is a backwards compatibility mode which uses
	Amino JSON and will be removed in the future.
    """
    SignMode_SIGN_MODE_LEGACY_AMINO_JSON = 127
    """
    SIGN_MODE_EIP_191 specifies the sign mode for EIP 191 signing on the Cosmos
	SDK. Ref: https:eips.ethereum.org/EIPS/eip-191
	
	Currently, SIGN_MODE_EIP_191 is registered as a SignMode enum variant,
	but is not implemented on the SDK by default. To enable EIP-191, you need
	to pass a custom `TxConfig` that has an implementation of
	`SignModeHandler` for EIP-191. The SDK may decide to fully support
	EIP-191 in the future.
	
	Since: cosmos-sdk 0.45.2
    """
    SignMode_SIGN_MODE_EIP_191 = 191
    """
    SIGN_MODE_EIP_712 specifies the sign mode for EIP 712 signing on the Cosmos
	SDK. Ref: https:eips.ethereum.org/EIPS/eip-712
    """
    SignMode_SIGN_MODE_EIP_712 = 712


@dataclass(eq=False, repr=False)
class SignerData(betterproto.Message):
    """
    SignerData is the specific information needed to sign a transaction that generally
    isn't included in the transaction body itself
    https://github.com/bnb-chain/greenfield-cosmos-sdk/blob/master/x/auth/signing/sign_mode_handler.go#L26
    """

    chain_id: str = betterproto.string_field(1)
    account_number: int = betterproto.uint32_field(2)
    sequence: int = betterproto.uint32_field(3)
    address: Optional[str] = betterproto.string_field(4)
    public_key: Optional[str] = betterproto.string_field(5)


@dataclass(eq=False, repr=False)
class SingleSignatureData(betterproto.Message):
    """
    SingleSignatureData represents the signature and SignMode of a single (non-multisig) signer
    https://github.com/bnb-chain/greenfield-cosmos-sdk/blob/master/types/tx/signing/signature_data.go#L15
    """

    sign_mode: SignModeData = betterproto.enum_field(1)
    signature: List[bytes] = betterproto.bytes_field(2)


@dataclass(eq=False, repr=False)
class SignatureV2(betterproto.Message):
    """
    SignatureV2 is a convenience type that is easier to use in application logic
    than the protobuf SignerInfo's and raw signature bytes. It goes beyond the
    first sdk.Signature types by supporting sign modes and explicitly nested
    multi-signatures. It is intended to be used for both building and verifying
    signatures.
    https://github.com/bnb-chain/greenfield-cosmos-sdk/blob/master/types/tx/signing/signature.go#L15
    """

    pub_key: bytes = betterproto.bytes_field(1)
    data: SingleSignatureData = betterproto.message_field(2)
    sequence: int = betterproto.uint32_field(3)


@dataclass(eq=False, repr=False)
class TxOption(betterproto.Message):
    """
    TxOption is the option for the transaction.
    """

    mode: BroadcastMode = betterproto.enum_field(1)
    no_simulate: bool = betterproto.bool_field(2)
    gas_limit: int = betterproto.int32_field(3)
    fee_amount: Coin = betterproto.message_field(4)
    nonce: int = betterproto.int32_field(5)
    fee_payer: str = betterproto.string_field(6)
    fee_granter: str = betterproto.string_field(7)
    tip: Tip = betterproto.message_field(8)
    memo: str = betterproto.string_field(9)


class BroadcastOption(BaseModel):
    sp_signature: Optional[str] = ""
    checksums: Optional[list[str]] = None
