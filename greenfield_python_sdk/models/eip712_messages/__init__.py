from greenfield_python_sdk.models.eip712_messages import (
    authz,
    bank,
    challenge,
    crosschain,
    distribution,
    feegrant,
    gov,
    group,
    payment,
    proposal,
    slashing,
    sp,
    staking,
    storage,
)

TYPES_MAP = {
    **bank.TYPES_MAP,
    **challenge.TYPES_MAP,
    **crosschain.TYPES_MAP,
    **distribution.TYPES_MAP,
    **feegrant.TYPES_MAP,
    **gov.TYPES_MAP,
    **staking.TYPES_MAP,
    **group.TYPES_MAP,
    **payment.TYPES_MAP,
    **proposal.TYPES_MAP,
    **sp.TYPES_MAP,
    **storage.TYPES_MAP,
    **authz.TYPES_MAP,
    **slashing.TYPES_MAP,
}

URL_TO_PROTOS_TYPE_MAP = {
    **feegrant.URL_TO_PROTOS_TYPE_MAP,
    **proposal.URL_TO_PROTOS_TYPE_MAP,
    **sp.URL_TO_PROTOS_TYPE_MAP,
    **storage.URL_TO_PROTOS_TYPE_MAP,
    **staking.URL_TO_PROTOS_TYPE_MAP,
}
