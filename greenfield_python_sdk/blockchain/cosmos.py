from grpclib.client import Channel

from greenfield_python_sdk.blockchain._cosmos import (
    auth,
    authz,
    bank,
    crosschain,
    distribution,
    evidence,
    feegrant,
    gov,
    mint,
    oracle,
    params,
    slashing,
    staking,
    tx,
    upgrade,
)


class Cosmos:
    def __init__(self, channel: Channel):
        self.auth = auth.Auth(channel)
        self.authz = authz.Authz(channel)
        self.bank = bank.Bank(channel)
        self.crosschain = crosschain.Crosschain(channel)
        self.distribution = distribution.Distribution(channel)
        self.evidence = evidence.Evidence(channel)
        self.feegrant = feegrant.FeeGrant(channel)
        self.gov = gov.Gov(channel)
        self.mint = mint.Mint(channel)
        self.params = params.Params(channel)
        self.slashing = slashing.Slashing(channel)
        self.staking = staking.Staking(channel)
        self.oracle = oracle.Oracle(channel)
        self.tx = tx.Tx(channel)
        self.upgrade = upgrade.Upgrade(channel)
