import logging
from typing import Optional

from grpclib.client import Channel

from greenfield_python_sdk.blockchain_client import BlockchainClient
from greenfield_python_sdk.config import GREENFIELD_VERSION, NetworkConfiguration
from greenfield_python_sdk.greenfield.account import Account as AccountInterface
from greenfield_python_sdk.greenfield.basic import Basic
from greenfield_python_sdk.greenfield.bucket import Bucket
from greenfield_python_sdk.greenfield.challenge import Challenge
from greenfield_python_sdk.greenfield.crosschain import CrossChain
from greenfield_python_sdk.greenfield.distribution import Distribution
from greenfield_python_sdk.greenfield.feegrant import FeeGrant
from greenfield_python_sdk.greenfield.group import Group
from greenfield_python_sdk.greenfield.object import Object
from greenfield_python_sdk.greenfield.payment import Payment
from greenfield_python_sdk.greenfield.proposal import Proposal
from greenfield_python_sdk.greenfield.storage_provider import StorageProvider
from greenfield_python_sdk.greenfield.validator import Validator
from greenfield_python_sdk.greenfield.virtual_group import VirtualGroup
from greenfield_python_sdk.key_manager import Account, KeyManager
from greenfield_python_sdk.storage_client import StorageClient

logger = logging.getLogger(__name__)


class GreenfieldClient:
    storage_client: StorageClient
    blockchain_client: BlockchainClient

    basic: Basic
    bucket: Bucket
    challenge: Challenge
    crosschain: CrossChain
    distribution: Distribution
    feegrant: FeeGrant
    group: Group
    object: Object
    payment: Payment
    proposal: Proposal
    storage_provider: StorageProvider
    validator: Validator
    virtual_group: VirtualGroup

    def __init__(
        self,
        key_manager: KeyManager,
        network_configuration: NetworkConfiguration,
        channel: Optional[Channel] = None,
    ):
        self.network_configuration = network_configuration
        self.key_manager = key_manager
        self.channel = channel

    async def __aenter__(self):
        self.blockchain_client = await BlockchainClient(
            network_configuration=self.network_configuration, key_manager=self.key_manager
        ).__aenter__()

        # Get the sp_endpoints for the storage client
        response = await self.blockchain_client.sp.get_storage_providers()
        sp_endpoints = {
            sp["operatorAddress"]: sp for sp in response.to_pydict()["sps"]
        }  # Transform the response to a dict with the operatorAddress as key

        self.storage_client = await StorageClient(key_manager=self.key_manager, sp_endpoints=sp_endpoints).__aenter__()

        # Embeded clients
        self.basic = Basic(self.blockchain_client)
        self.account = AccountInterface(self.blockchain_client, self.basic)
        self.bucket = Bucket(self.blockchain_client, self.key_manager, self.storage_client)
        self.challenge = Challenge(self.blockchain_client, self.storage_client)
        self.crosschain = CrossChain(self.blockchain_client, self.storage_client)
        self.distribution = Distribution(self.blockchain_client, self.storage_client)
        self.feegrant = FeeGrant(self.blockchain_client, self.storage_client)
        self.group = Group(self.blockchain_client, self.storage_client)
        self.object = Object(self.blockchain_client, self.key_manager, self.storage_client)
        self.payment = Payment(self.blockchain_client, self.storage_client)
        self.proposal = Proposal(self.blockchain_client, self.storage_client)
        self.storage_provider = StorageProvider(self.blockchain_client, self.key_manager, self.storage_client)
        self.validator = Validator(self.blockchain_client, self.storage_client, self.basic, self.account)
        self.virtual_group = VirtualGroup(self.blockchain_client, self.key_manager)

        return self

    async def async_init(self):
        await self.check_node_version()
        await self.sync_account()

    async def check_node_version(self):
        # Check the node version
        node_version = await self.basic.get_greenfield_node_version()
        if node_version != GREENFIELD_VERSION:
            logger.warning(f"Node version mismatch. Expected: {GREENFIELD_VERSION}, got: {node_version}")

    async def sync_account(self):
        # Add the account number and sequence to the key manager
        account = await self.account.get_account(address=self.key_manager.address)
        self.key_manager.account.next_sequence = account.sequence
        self.key_manager.account.account_number = account.account_number

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.storage_client.close()
        await self.blockchain_client.close()

    async def get_default_account(self) -> Account:
        return self.key_manager.account

    async def set_default_account(self, account: Account) -> None:
        self.key_manager.account = account
        await self.sync_account()
