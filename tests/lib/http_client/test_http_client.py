import io

import pytest
from pytest_httpx import HTTPXMock

from lib.http_client import BaseHTTPClient


class TestGet:
    @pytest.mark.asyncio
    async def test_get(
        self, base_http_client: BaseHTTPClient, httpx_mock: HTTPXMock, base_url: str
    ) -> None:
        httpx_mock.add_response(
            method="GET", url=f"{base_url}/example/path", json={"example": "response"}
        )
        response = await base_http_client.get("example/path")
        assert response == {"example": "response"}

    @pytest.mark.asyncio
    async def test_get_with_params_in_url(
        self, base_http_client: BaseHTTPClient, httpx_mock: HTTPXMock, base_url: str
    ) -> None:
        httpx_mock.add_response(
            method="GET",
            url=f"{base_url}/example/path?my=example&list_param=1&list_param=2",
            json={"example": "response"},
        )
        response = await base_http_client.get(
            "example/path?my=example&list_param=1&list_param=2",
        )
        assert response == {"example": "response"}

    @pytest.mark.asyncio
    async def test_get_with_params(
        self, base_http_client: BaseHTTPClient, httpx_mock: HTTPXMock, base_url: str
    ) -> None:
        httpx_mock.add_response(
            method="GET",
            url=f"{base_url}/example/path?my=example&list_param=1&list_param=2",
            json={"example": "response"},
        )
        response = await base_http_client.get(
            "example/path", params={"my": "example", "list_param": ["1", "2"]}
        )
        assert response == {"example": "response"}


class TestPost:
    @pytest.mark.asyncio
    async def test_post(
        self, base_http_client: BaseHTTPClient, httpx_mock: HTTPXMock, base_url: str
    ) -> None:
        httpx_mock.add_response(
            method="POST",
            url=f"{base_url}/example/path",
            json={"example": "response"},
            match_json=None,
        )
        response = await base_http_client.post("/example/path")
        assert response == {"example": "response"}

    @pytest.mark.asyncio
    async def test_post_with_json(
        self, base_http_client: BaseHTTPClient, httpx_mock: HTTPXMock, base_url: str
    ) -> None:
        httpx_mock.add_response(
            method="POST",
            url=f"{base_url}/example/path",
            json={"example": "response"},
            match_json={"create": "example"},
        )
        response = await base_http_client.post(
            "example/path", json={"create": "example"}
        )
        assert response == {"example": "response"}

    @pytest.mark.asyncio
    async def test_post_with_json_and_params(
        self, base_http_client: BaseHTTPClient, httpx_mock: HTTPXMock, base_url: str
    ) -> None:
        httpx_mock.add_response(
            method="POST",
            url=f"{base_url}/example/path?my=example&list_param=1&list_param=2",
            json={"example": "response"},
            match_json={"create": "example"},
        )
        response = await base_http_client.post(
            "example/path",
            json={"create": "example"},
            params={"my": "example", "list_param": ["1", "2"]},
        )
        assert response == {"example": "response"}

    @pytest.mark.asyncio
    async def test_post_files(
        self, base_http_client: BaseHTTPClient, httpx_mock: HTTPXMock, base_url: str
    ) -> None:
        httpx_mock.add_response(
            method="POST",
            url=f"{base_url}/example/path?my=example&list_param=1&list_param=2",
            json={"example": "response"},
        )
        response = await base_http_client.post(
            "example/path",
            json={"create": "example"},
            params={"my": "example", "list_param": ["1", "2"]},
            files={
                "file": (
                    "example_file.json",
                    io.BytesIO(b'{"example": "json"}'),
                    "application/json",
                )
            },
        )
        assert response == {"example": "response"}


class TestPut:
    @pytest.mark.asyncio
    async def test_put(
        self, base_http_client: BaseHTTPClient, httpx_mock: HTTPXMock, base_url: str
    ) -> None:
        httpx_mock.add_response(
            method="PUT",
            url=f"{base_url}/example/path",
            json={"example": "response"},
            match_json=None,
        )
        response = await base_http_client.put("/example/path")
        assert response == {"example": "response"}

    @pytest.mark.asyncio
    async def test_put_with_json(
        self, base_http_client: BaseHTTPClient, httpx_mock: HTTPXMock, base_url: str
    ) -> None:
        httpx_mock.add_response(
            method="PUT",
            url=f"{base_url}/example/path",
            json={"example": "response"},
            match_json={"create": "example"},
        )
        response = await base_http_client.put(
            "example/path", json={"create": "example"}
        )
        assert response == {"example": "response"}

    @pytest.mark.asyncio
    async def test_put_with_json_and_params(
        self, base_http_client: BaseHTTPClient, httpx_mock: HTTPXMock, base_url: str
    ) -> None:
        httpx_mock.add_response(
            method="PUT",
            url=f"{base_url}/example/path?my=example&list_param=1&list_param=2",
            json={"example": "response"},
            match_json={"create": "example"},
        )
        response = await base_http_client.put(
            "example/path",
            json={"create": "example"},
            params={"my": "example", "list_param": ["1", "2"]},
        )
        assert response == {"example": "response"}


class TestPatch:
    @pytest.mark.asyncio
    async def test_patch(
        self, base_http_client: BaseHTTPClient, httpx_mock: HTTPXMock, base_url: str
    ) -> None:
        httpx_mock.add_response(
            method="PATCH",
            url=f"{base_url}/example/path",
            json={"example": "response"},
            match_json=None,
        )
        response = await base_http_client.patch("/example/path")
        assert response == {"example": "response"}

    @pytest.mark.asyncio
    async def test_patch_with_json(
        self, base_http_client: BaseHTTPClient, httpx_mock: HTTPXMock, base_url: str
    ) -> None:
        httpx_mock.add_response(
            method="PATCH",
            url=f"{base_url}/example/path",
            json={"example": "response"},
            match_json={"create": "example"},
        )
        response = await base_http_client.patch(
            "example/path", json={"create": "example"}
        )
        assert response == {"example": "response"}

    @pytest.mark.asyncio
    async def test_patch_with_json_and_params(
        self, base_http_client: BaseHTTPClient, httpx_mock: HTTPXMock, base_url: str
    ) -> None:
        httpx_mock.add_response(
            method="PATCH",
            url=f"{base_url}/example/path?my=example&list_param=1&list_param=2",
            json={"example": "response"},
            match_json={"create": "example"},
        )
        response = await base_http_client.patch(
            "example/path",
            json={"create": "example"},
            params={"my": "example", "list_param": ["1", "2"]},
        )
        assert response == {"example": "response"}


class TestDelete:
    @pytest.mark.asyncio
    async def test_delete(
        self, base_http_client: BaseHTTPClient, httpx_mock: HTTPXMock, base_url: str
    ) -> None:
        httpx_mock.add_response(method="DELETE", url=f"{base_url}/example/path")
        response = await base_http_client.delete("/example/path")
        assert response is None

    @pytest.mark.asyncio
    async def test_delete_with_params(
        self, base_http_client: BaseHTTPClient, httpx_mock: HTTPXMock, base_url: str
    ) -> None:
        httpx_mock.add_response(
            method="DELETE",
            url=f"{base_url}/example/path?my=example&list_param=1&list_param=2",
        )
        response = await base_http_client.delete(
            "example/path", params={"my": "example", "list_param": ["1", "2"]}
        )
        assert response is None
