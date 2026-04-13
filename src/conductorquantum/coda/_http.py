"""Shared HTTP utilities for Coda sync and async clients."""

from __future__ import annotations

import json
import os
import time
from typing import Any

import httpx

from conductorquantum.coda.errors import CodaAPIError, CodaAuthError, CodaTimeoutError

DEFAULT_BASE_URL = "https://api.conductorquantum.com/v0"
DEFAULT_TIMEOUT = 120.0
MAX_RETRIES = 2
INITIAL_RETRY_DELAY = 0.5
RETRYABLE_STATUS_CODES = {429, 408, 500, 502, 503, 504}


def api_base_url_from_env() -> str:
    """Resolve the REST API base URL from the environment.

    Precedence:

    1. ``CODA_API_BASE_URL`` — full base URL, used as given (trailing ``/`` stripped),
       e.g. ``https://api.conductorquantum.com/v0``.
    2. ``CODA_BASE_URL`` — origin; ``/v0`` is appended unless the path already ends with
       ``/v0``.
    3. :data:`DEFAULT_BASE_URL` if neither is set.

    The Next.js app on ``http://localhost:3000`` is the web UI and does **not** serve
    the public ``/v0`` HTTP API; use ``CODA_API_BASE_URL`` to target a real API host.
    """
    api_base = os.environ.get("CODA_API_BASE_URL", "").strip()
    if api_base:
        return api_base.rstrip("/")
    origin = os.environ.get("CODA_BASE_URL", "").strip()
    if not origin:
        return DEFAULT_BASE_URL
    origin = origin.rstrip("/")
    if origin.endswith("/v0"):
        return origin
    return f"{origin}/v0"


def build_headers(token: str, sdk_version: str) -> dict[str, str]:
    """Build default request headers."""
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": f"conductorquantum-python/{sdk_version}",
    }


def _should_retry(status_code: int) -> bool:
    return status_code in RETRYABLE_STATUS_CODES


def _raise_for_status(response: httpx.Response) -> None:
    """Raise appropriate exception for non-success responses (not 2xx)."""
    if response.is_success:
        return

    status = response.status_code
    try:
        body = response.json()
    except Exception:
        body = None

    if body and isinstance(body, dict):
        detail = str(body.get("detail", "") or body.get("error", "") or body)
    else:
        detail = (response.text or "")[:500]

    if status in (301, 302, 303, 307, 308):
        location = response.headers.get("location", "")
        base = detail.strip() if detail else f"HTTP {status} redirect"
        tail = f" Location: {location}" if location else ""
        combined = (base + tail).lower()
        hint = ""
        if "login" in combined:
            hint = (
                " Redirect to login usually means the Next.js web app (e.g. :3000), not the Coda /v0 HTTP API. "
                "Set CODA_API_BASE_URL to https://api.conductorquantum.com/v0 (or your API gateway)."
            )
        detail = base + tail + (f" {hint}" if hint else "")

    if not detail.strip():
        detail = f"HTTP {status}"

    if status in (401, 403):
        raise CodaAuthError(status, detail, body if isinstance(body, dict) else None)
    raise CodaAPIError(status, detail, body if isinstance(body, dict) else None)


def parse_json(response: httpx.Response) -> dict[str, Any]:
    """Parse response JSON, raising on error."""
    _raise_for_status(response)
    try:
        result: dict[str, Any] = response.json()
    except json.JSONDecodeError as exc:
        raw = response.text or ""
        preview = raw[:400].replace("\n", "\\n")
        ct = response.headers.get("content-type", "")
        url = str(response.request.url)
        hint = ""
        if not raw.strip():
            hint = (
                " Empty body often means the host is not the Coda API "
                "(e.g. Next.js on :3000 has no /v0). Set CODA_API_BASE_URL to the real API base."
            )
        elif raw.lstrip().startswith("<"):
            hint = " Response looks like HTML, not the JSON API; check CODA_API_BASE_URL / base_url."
        detail = (
            f"Response body is not JSON ({exc.msg} at char {exc.pos}). "
            f"url={url} status={response.status_code} content-type={ct!r} body_preview={preview!r}.{hint}"
        )
        raise CodaAPIError(response.status_code, detail, None) from exc
    return result


def retry_delay(attempt: int) -> float:
    """Exponential backoff delay for retries."""
    delay: float = min(INITIAL_RETRY_DELAY * (2**attempt), 10.0)
    return delay


def sync_request(
    client: httpx.Client,
    method: str,
    path: str,
    *,
    json: dict[str, Any] | None = None,
    max_retries: int = MAX_RETRIES,
) -> httpx.Response:
    """Make a sync HTTP request with retries."""
    last_exc: Exception | None = None
    for attempt in range(max_retries + 1):
        try:
            response = client.request(method, path, json=json)
            if _should_retry(response.status_code) and attempt < max_retries:
                time.sleep(retry_delay(attempt))
                continue
            return response
        except httpx.TimeoutException as e:
            last_exc = e
            if attempt < max_retries:
                time.sleep(retry_delay(attempt))
                continue
            raise CodaTimeoutError(str(e)) from e
        except httpx.HTTPError as e:
            last_exc = e
            if attempt < max_retries:
                time.sleep(retry_delay(attempt))
                continue
            raise

    assert last_exc is not None
    raise last_exc


async def async_request(
    client: httpx.AsyncClient,
    method: str,
    path: str,
    *,
    json: dict[str, Any] | None = None,
    max_retries: int = MAX_RETRIES,
) -> httpx.Response:
    """Make an async HTTP request with retries."""
    import asyncio

    last_exc: Exception | None = None
    for attempt in range(max_retries + 1):
        try:
            response = await client.request(method, path, json=json)
            if _should_retry(response.status_code) and attempt < max_retries:
                await asyncio.sleep(retry_delay(attempt))
                continue
            return response
        except httpx.TimeoutException as e:
            last_exc = e
            if attempt < max_retries:
                await asyncio.sleep(retry_delay(attempt))
                continue
            raise CodaTimeoutError(str(e)) from e
        except httpx.HTTPError as e:
            last_exc = e
            if attempt < max_retries:
                await asyncio.sleep(retry_delay(attempt))
                continue
            raise

    assert last_exc is not None
    raise last_exc
