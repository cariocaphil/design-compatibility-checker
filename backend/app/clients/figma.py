"""Figma REST API client (PROJECT_SPEC.md section 13).

Isolates the only network boundary for the Figma input path so that
`app/services/figma.py` can remain pure, deterministic, and easily testable
(PROJECT_SPEC.md section 9: external providers isolated behind clients).

The access token is passed in explicitly rather than read from
`app.core.config` here, keeping this client trivially mockable and leaving
"is Figma configured" decisions to whichever layer constructs it.
"""

import httpx

FIGMA_API_BASE_URL = "https://api.figma.com/v1"


class FigmaAPIError(Exception):
    """Raised when the Figma API cannot be reached or returns an error response."""


class FigmaClient:
    """Thin async wrapper around the Figma "get file" REST endpoint."""

    def __init__(self, http_client: httpx.AsyncClient, access_token: str) -> None:
        self._http_client = http_client
        self._access_token = access_token

    async def get_file(self, file_key: str) -> dict:
        """Fetch the raw Figma file document graph for `file_key`.

        Raises `FigmaAPIError` on network failure, a non-2xx response, or a
        response body that cannot be parsed as JSON. Never logs the access
        token (PROJECT_SPEC.md section 25).
        """
        url = f"{FIGMA_API_BASE_URL}/files/{file_key}"

        try:
            response = await self._http_client.get(
                url, headers={"X-Figma-Token": self._access_token}
            )
        except httpx.HTTPError as exc:
            raise FigmaAPIError(f"Failed to reach the Figma API: {exc}") from exc

        if response.status_code != httpx.codes.OK:
            raise FigmaAPIError(
                f"Figma API returned an error response (status {response.status_code})"
            )

        try:
            return response.json()
        except ValueError as exc:
            raise FigmaAPIError("Figma API returned a non-JSON response") from exc
