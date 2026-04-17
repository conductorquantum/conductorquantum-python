"""Regression tests for HttpClient / AsyncHttpClient retry behavior.

The retry path previously did not forward ``data`` or ``force_multipart``
to the recursive call, so retried multipart uploads were sent with an
empty body.

HttpClient.request starts with ``retries=2`` and recurses on retry with
``retries + 1``, so ``max_retries=3`` yields exactly one retry.
"""

from __future__ import annotations

import asyncio
import time
import typing

import httpx
import pytest
from conductorquantum.core.http_client import AsyncHttpClient, HttpClient


def _recording_handler(
    responses: typing.List[httpx.Response],
) -> typing.Tuple[typing.Callable[[httpx.Request], httpx.Response], typing.List[httpx.Request]]:
    captured: typing.List[httpx.Request] = []
    iterator = iter(responses)

    def handler(request: httpx.Request) -> httpx.Response:
        # Force the body to be read so tests can inspect ``request.content``.
        request.read()
        captured.append(request)
        return next(iterator)

    return handler, captured


def _sync_client(handler: typing.Callable[[httpx.Request], httpx.Response]) -> HttpClient:
    return HttpClient(
        httpx_client=httpx.Client(transport=httpx.MockTransport(handler)),
        base_timeout=lambda: 5.0,
        base_headers=lambda: {},
        base_url=lambda: "http://example.test",
    )


def _async_client(handler: typing.Callable[[httpx.Request], httpx.Response]) -> AsyncHttpClient:
    return AsyncHttpClient(
        httpx_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
        base_timeout=lambda: 5.0,
        base_headers=lambda: {},
        base_url=lambda: "http://example.test",
    )


def test_retry_preserves_multipart_data_and_files(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(time, "sleep", lambda _seconds: None)

    handler, captured = _recording_handler(
        [httpx.Response(429), httpx.Response(200, json={"ok": True})]
    )
    client = _sync_client(handler)

    response = client.request(
        path="models",
        method="POST",
        data={"model": "coulomb-blockade-peak-detector-v1"},
        files={"data": ("payload.bin", b"0123456789", "application/octet-stream")},
        request_options={"max_retries": 3},
    )

    assert response.status_code == 200
    assert len(captured) == 2

    for attempt, request in enumerate(captured):
        content_type = request.headers.get("content-type", "")
        assert content_type.startswith("multipart/form-data"), (
            f"attempt {attempt}: expected multipart request, got {content_type!r}"
        )
        body = request.content
        assert b"coulomb-blockade-peak-detector-v1" in body, (
            f"attempt {attempt}: retried request dropped the `data` field"
        )
        assert b"0123456789" in body, (
            f"attempt {attempt}: retried request dropped the uploaded file bytes"
        )


def test_retry_preserves_force_multipart_flag(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(time, "sleep", lambda _seconds: None)

    handler, captured = _recording_handler(
        [httpx.Response(429), httpx.Response(200, json={"ok": True})]
    )
    client = _sync_client(handler)

    client.request(
        path="models",
        method="POST",
        force_multipart=True,
        request_options={"max_retries": 3},
    )

    assert len(captured) == 2
    for attempt, request in enumerate(captured):
        content_type = request.headers.get("content-type", "")
        assert content_type.startswith("multipart/form-data"), (
            f"attempt {attempt}: force_multipart was lost on retry (got {content_type!r})"
        )


async def test_async_retry_preserves_multipart_data_and_files(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def _noop_sleep(_seconds: float) -> None:
        return None

    monkeypatch.setattr(asyncio, "sleep", _noop_sleep)

    handler, captured = _recording_handler(
        [httpx.Response(429), httpx.Response(200, json={"ok": True})]
    )
    client = _async_client(handler)

    response = await client.request(
        path="models",
        method="POST",
        data={"model": "coulomb-blockade-peak-detector-v1"},
        files={"data": ("payload.bin", b"abcdef", "application/octet-stream")},
        request_options={"max_retries": 3},
    )

    assert response.status_code == 200
    assert len(captured) == 2

    for attempt, request in enumerate(captured):
        content_type = request.headers.get("content-type", "")
        assert content_type.startswith("multipart/form-data"), (
            f"attempt {attempt}: expected multipart request, got {content_type!r}"
        )
        body = request.content
        assert b"coulomb-blockade-peak-detector-v1" in body
        assert b"abcdef" in body
