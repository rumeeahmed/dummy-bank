from typing import AsyncGenerator, Generator

from httpx import URL, Auth, Request, Response


class QueryParamAuth(Auth):
    """
    HTTPX authentication for APIs where an API Key/Token is required in the query params
    """

    def __init__(self, key: str, token: str) -> None:
        self._key = key
        self._token = token

    def sync_auth_flow(self, request: Request) -> Generator[Request, Response, None]:
        request.url = self._build_url(request)
        yield request

    async def async_auth_flow(
        self, request: Request
    ) -> AsyncGenerator[Request, Response]:
        request.url = self._build_url(request)
        yield request

    def _build_url(self, request: Request) -> URL:
        print(request.url)
        return URL(f"{request.url}&{self._key}={self._token}")
