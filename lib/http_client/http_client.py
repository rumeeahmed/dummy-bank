from typing import Any
from urllib.parse import parse_qs, urlparse

import httpx


class BaseHTTPClient:
    def __init__(
        self,
        base_url: str,
        authorization: httpx.Auth | None = None,
        timeout: float | int = 5.0,
    ) -> None:
        self.client = httpx.AsyncClient(
            base_url=base_url, timeout=timeout, auth=authorization
        )

    async def get(
        self, path: str, params: dict[str, str | list[str]] | None = None
    ) -> Any:
        return await self._make_request("GET", path, params=params)

    async def post(
        self,
        path: str,
        json: Any = None,
        files: httpx._types.RequestFiles | None = None,
        params: dict[str, str | list[str]] | None = None,
    ) -> Any:
        return await self._make_request(
            "POST", path, json=json, files=files, params=params
        )

    async def put(
        self,
        path: str,
        json: Any = None,
        params: dict[str, str | list[str]] | None = None,
    ) -> Any:
        return await self._make_request("PUT", path, json=json, params=params)

    async def patch(
        self,
        path: str,
        json: Any = None,
        params: dict[str, str | list[str]] | None = None,
    ) -> Any:
        return await self._make_request("PATCH", path, json=json, params=params)

    async def delete(
        self, path: str, params: dict[str, str | list[str]] | None = None
    ) -> Any:
        return await self._make_request("DELETE", path, params=params)

    async def _make_request(
        self,
        method: str,
        path: str,
        params: dict[str, str | list[str]] | None = None,
        additional_headers: dict[str, str] | None = None,
        json: Any = None,
        files: httpx._types.RequestFiles | None = None,
    ) -> Any:
        if not additional_headers:
            additional_headers = {}

        if not params:
            params = {}

        if not path.startswith("/"):
            path = f"/{path}"

        query_string = urlparse(path).query
        path_queries = parse_qs(query_string)
        params = {**path_queries, **params}
        response = await self.client.request(
            method=method,
            url=path,
            params=params,
            json=json,
            files=files,
            headers=additional_headers,
        )

        response.raise_for_status()

        if response.status_code == 204 or response.text == "":
            return None

        return response.json()
