import pytest
from httpx import URL, Request

from lib.authentication.query_param_auth import QueryParamAuth


class TestQueryParamAuth:
    @pytest.mark.asyncio
    async def test_async_auth_flow(self, google_maps_api_key: str) -> None:
        auth = QueryParamAuth(key="key", token=google_maps_api_key)
        request = Request("GET", "https://api.example.com/data?existing_param=value")

        auth_flow = auth.async_auth_flow(request)
        updated_request = await auth_flow.__anext__()

        assert updated_request.url == URL(
            f"https://api.example.com/data?existing_param=value&key={google_maps_api_key}"
        )

    def test_sync(self, google_maps_api_key: str) -> None:
        auth = QueryParamAuth(key="key", token=google_maps_api_key)
        request = Request("GET", "https://api.example.com/data?existing_param=value")

        auth_flow = auth.sync_auth_flow(request)
        updated_request = next(auth_flow)

        assert updated_request.url == URL(
            f"https://api.example.com/data?existing_param=value&key={google_maps_api_key}"
        )
