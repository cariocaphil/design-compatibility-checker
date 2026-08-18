from collections.abc import Callable

import httpx
import pytest

from app.clients.figma import FigmaAPIError, FigmaClient


def _client(
    handler: Callable[[httpx.Request], httpx.Response], token: str = "test-token"
) -> FigmaClient:
    transport = httpx.MockTransport(handler)
    http_client = httpx.AsyncClient(transport=transport)
    return FigmaClient(http_client=http_client, access_token=token)


async def test_get_file_returns_parsed_json_on_success() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"document": {"children": []}})

    result = await _client(handler).get_file("abc123")

    assert result == {"document": {"children": []}}


async def test_get_file_requests_the_expected_url() -> None:
    requested_urls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requested_urls.append(str(request.url))
        return httpx.Response(200, json={})

    await _client(handler).get_file("abc123")

    assert requested_urls == ["https://api.figma.com/v1/files/abc123"]


async def test_get_file_sends_figma_token_header() -> None:
    captured_headers: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured_headers.update(request.headers)
        return httpx.Response(200, json={})

    await _client(handler, token="secret-token").get_file("abc123")

    assert captured_headers["x-figma-token"] == "secret-token"


async def test_get_file_raises_figma_api_error_on_non_200_response() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404, json={"status": 404, "err": "Not found"})

    with pytest.raises(FigmaAPIError):
        await _client(handler).get_file("missing-key")


async def test_get_file_raises_figma_api_error_on_network_failure() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused")

    with pytest.raises(FigmaAPIError):
        await _client(handler).get_file("abc123")


async def test_get_file_raises_figma_api_error_on_non_json_body() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=b"not json")

    with pytest.raises(FigmaAPIError):
        await _client(handler).get_file("abc123")
