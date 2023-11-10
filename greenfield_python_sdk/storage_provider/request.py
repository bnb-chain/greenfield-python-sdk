import logging
import re
import urllib.request
from typing import Any, Dict, Optional, Union
from urllib.parse import urlparse

import aiohttp
import html_to_json

from greenfield_python_sdk.key_manager import KeyManager
from greenfield_python_sdk.models.const import USER_AGENT
from greenfield_python_sdk.models.request import RequestMeta
from greenfield_python_sdk.storage_provider.utils import (
    convert_key,
    convert_value,
    generate_headers,
    generate_url,
    generate_url_chunks,
)

logger = logging.getLogger(__name__)


class Client:
    def __init__(
        self,
        key_manager: KeyManager,
        sp_endpoints: dict,
    ):
        self.key_manager: KeyManager = key_manager
        self.sp_endpoints: dict = sp_endpoints

        self.headers = {"accept": "application/json", "User-Agent": USER_AGENT}
        self.session: aiohttp.ClientSession

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    @property
    def open(self) -> bool:
        if self.scheme not in ["http", "https"]:
            raise ValueError(f"Invalid scheme: {self.scheme}")
        url_open = urllib.request.urlopen(self.scheme + self.domain_name).getcode()
        if url_open == 200:
            return True
        return False

    async def fetch(
        self,
        method: str,
        url: str,
        headers: dict = None,
        data: Optional[Any] = None,
        type: Optional[str] = None,
    ) -> Union[str, aiohttp.ClientResponse]:
        if type == "body":
            async with self.session.request(method, url, headers=headers) as response:
                return await response.text()
        else:
            if method == "GET":
                response = await self.session.get(url, headers=headers)
            elif method == "PUT":
                response = await self.session.put(url, data=data, headers=headers)
            if response.status >= 400:
                converted_data = {
                    convert_key(key): convert_value(key, value) if value[0] else ""
                    for key, value in html_to_json.convert(await response.text()).items()
                }
                if "failed to get user buckets" in converted_data["error"]["message"]:
                    return response
                raise Exception(f"Error with response status: \n{await response.text()}")
            return response

    async def _get_sp_url_by_addr(self, address: str, bucket_name: str = "") -> str:
        if self.sp_endpoints and address in self.sp_endpoints:
            return (
                self.sp_endpoints[address]["endpoint"]
                if bucket_name == ""
                else self.set_bucket_url(address, bucket_name)
            )
        else:
            raise KeyError(f"Address {address} not found in sp_endpoints")

    async def _get_sp_url_by_id(self, id: int) -> str:
        if self.sp_endpoints:
            for key in self.sp_endpoints:
                if self.sp_endpoints[key]["id"] == id:
                    return self.sp_endpoints[key]["endpoint"]
        else:
            raise KeyError(f"Id {id} not found in sp_endpoints")

    async def _get_in_service_sp(self):
        if self.sp_endpoints:
            return self.sp_endpoints[list(self.sp_endpoints.keys())[0]]["endpoint"]
        else:
            raise KeyError("No sp in service")

    def set_bucket_url(self, address: str, bucket_name: str) -> str:
        url = urlparse(self.sp_endpoints[address]["endpoint"])
        if url.scheme not in ["http", "https"]:
            raise ValueError(f"Invalid scheme: {url.scheme}")
        return url.scheme + "://" + bucket_name + "." + url.netloc

    async def prepare_request(
        self,
        base_url: str,
        request_metadata: RequestMeta,
        query_parameters: Dict[str, Any] = None,
        endpoint: str = None,
        is_admin_api: bool = False,
        body: Optional[Any] = None,
    ) -> aiohttp.ClientResponse:
        url = generate_url(
            base_url=base_url,
            endpoint=endpoint,
            query_parameters=query_parameters,
            is_admin_api=is_admin_api,
            object_name=request_metadata["object_name"],
            bucket_name=request_metadata["bucket_name"],
        )
        request_metadata["url"] = url

        relative_path, query_str = generate_url_chunks(
            endpoint=endpoint,
            query_parameters=query_parameters,
            is_admin_api=is_admin_api,
            object_name=request_metadata["object_name"],
        )
        request_metadata["relative_path"] = relative_path
        request_metadata["query_str"] = query_str

        headers = await generate_headers(metadata=request_metadata, key_manager=self.key_manager)

        return await self.fetch(method=request_metadata["method"], url=url, headers=headers, data=body)

    async def get_url(self, endpoint: str, sp_address: str) -> str:
        if endpoint == "" and sp_address == "":
            return await self._get_in_service_sp()
        elif endpoint != "":
            if bool(re.search(r"^(https?://)", endpoint)) is False:
                return "https://" + endpoint
            return endpoint
        elif sp_address != "":
            return await self._get_sp_url_by_addr(sp_address)

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

    async def close(self):
        if self.session:
            await self.session.close()
