from typing import List, Tuple

import aiohttp
from eth_utils import to_checksum_address

from greenfield_python_sdk.blockchain.utils import parse_account, parse_module_account
from greenfield_python_sdk.blockchain_client import BlockchainClient
from greenfield_python_sdk.greenfield.basic import Basic
from greenfield_python_sdk.models.account import PaginationParams
from greenfield_python_sdk.protos.cosmos.auth.v1beta1 import (
    BaseAccount,
    ModuleAccount,
    QueryAccountRequest,
    QueryModuleAccountByNameRequest,
)
from greenfield_python_sdk.protos.cosmos.bank.v1beta1 import MsgSend, QueryBalanceRequest
from greenfield_python_sdk.protos.cosmos.base.query.v1beta1 import PageResponse as PaginationResponse
from greenfield_python_sdk.protos.cosmos.base.v1beta1 import Coin
from greenfield_python_sdk.protos.greenfield.payment import (
    MsgCreatePaymentAccount,
    PaymentAccount,
    QueryPaymentAccountRequest,
    QueryPaymentAccountsByOwnerRequest,
)


class Account:
    blockchain_client: BlockchainClient
    basic: Basic

    def __init__(self, blockchain_client, basic):
        self.blockchain_client = blockchain_client
        self.basic = basic
        self.headers = {"accept": "application/json"}

    async def get_account(self, address: str) -> BaseAccount:
        address = to_checksum_address(address)
        response = await self.blockchain_client.cosmos.auth.get_account(QueryAccountRequest(address=address))
        account = await parse_account(response)
        return account

    async def create_payment_account(self, address: str, fee=None):
        address = to_checksum_address(address)
        message = MsgCreatePaymentAccount(creator=address)
        tx_hash = await self.blockchain_client.broadcast_message(
            message=message, type_url="/greenfield.payment.MsgCreatePaymentAccount", fee=fee
        )

        return tx_hash

    async def get_module_account_by_name(self, name: str) -> ModuleAccount:
        request = QueryModuleAccountByNameRequest(name=name)
        response = await self.blockchain_client.cosmos.auth.get_module_account_by_name(request)
        account = await parse_module_account(response.account)
        return account

    async def get_module_accounts(self) -> List[ModuleAccount]:
        response = await self.blockchain_client.cosmos.auth.get_module_accounts()
        accounts = []
        for account in response.accounts:
            accounts.append(await parse_module_account(account))
        return accounts

    async def get_account_balance(self, address: str, denom: str = "BNB") -> int:
        address = to_checksum_address(address)
        request = QueryBalanceRequest(address=address, denom=denom)
        response = await self.blockchain_client.cosmos.bank.get_balance(request)
        return int(response.balance.amount)

    async def transfer(self, from_address: str, to_address: str, amounts: List[Coin]) -> str:
        from_address = to_checksum_address(from_address)
        to_address = to_checksum_address(to_address)

        message = MsgSend(from_address=from_address, to_address=to_address, amount=amounts)

        response = await self.blockchain_client.broadcast_message(
            message=message, type_url="/cosmos.bank.v1beta1.MsgSend"
        )
        return response

    async def multi_transfer(self, inputs: list, outputs: list) -> str:
        # TODO: implement
        raise NotImplementedError

    async def get_payment_account(self, address: str) -> PaymentAccount:
        addr = to_checksum_address(address)
        request = QueryPaymentAccountRequest(addr)
        response = await self.blockchain_client.payment.get_payment_account(request)
        return response.payment_account

    async def get_payment_accounts_by_owner(self, owner: str) -> List[str]:
        owner = to_checksum_address(owner)
        request = QueryPaymentAccountsByOwnerRequest(owner)
        response = await self.blockchain_client.payment.get_payment_accounts_by_owner(request)
        return response.payment_accounts

    async def get_all_payment_accounts(self, pagination: PaginationParams = None) -> List[PaymentAccount]:
        endpoint = "/greenfield/payment/payment_accounts"
        if pagination:
            query_params = "&".join(
                [
                    f"pagination.{field}={value if field != 'key' else value.decode()}"
                    for field, value in pagination.__dict__.items()
                    if value is not None
                ]
            )
            if query_params:
                endpoint += f"?{query_params}"
        payment_accounts = []
        pagination = b""

        async with aiohttp.ClientSession() as session:
            res = await session.get(self.blockchain_client.channel.base_url + endpoint, headers=self.headers)
            payment_accounts = [PaymentAccount(**account) for account in (await res.json())["payment_accounts"]]
            pagination = PaginationResponse(**(await res.json())["pagination"])

        return payment_accounts, pagination
