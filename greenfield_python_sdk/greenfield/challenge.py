from typing import Any, List

from greenfield_python_sdk.blockchain_client import BlockchainClient
from greenfield_python_sdk.protos.greenfield.challenge import MsgSubmit
from greenfield_python_sdk.storage_client import StorageClient


class Challenge:
    def __init__(self, blockchain_client: BlockchainClient, storage_client: StorageClient):
        self.blockchain_client = blockchain_client
        self.storage_client = storage_client

    async def get_challenge_info(self):
        raise NotImplementedError

    async def submit_challenge(
        self,
        challenger_address: str,
        sp_operator_address: str,
        bucket_name: str,
        object_name: str,
        random_index: bool,
        segment_index: int,
    ) -> str:
        message = MsgSubmit(
            challenger=challenger_address,
            sp_operator_address=sp_operator_address,
            bucket_name=bucket_name,
            object_name=object_name,
            random_index=random_index,
            segment_index=segment_index,
        )
        tx_response = await self.blockchain_client.broadcast_message(
            message=message, type_url="/greenfield.challenge.MsgSubmit"
        )

        return tx_response

    async def attest_challenge(self):
        raise NotImplementedError

    async def get_latest_attested_challenges(self) -> List[int]:
        response = await self.blockchain_client.challenge.get_latest_attested_challenges()
        return response.challenges

    async def get_inturn_attestation_submitter(self) -> Any:
        response = await self.blockchain_client.challenge.get_inturn_attestation_submitter()
        return response

    async def get_challenge_params(self) -> Any:
        response = await self.blockchain_client.challenge.get_params()
        return response.params
