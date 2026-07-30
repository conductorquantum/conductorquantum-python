"""Tests for the default retry behaviour installed by ``_retry``."""

from __future__ import annotations

import typing

import httpx
import pytest

from conductorquantum import ConductorQuantum
from conductorquantum._retry import DEFAULT_MAX_RETRIES, install_default_retries

TOKEN = "test-token"


class _Recorder:
    """Stands in for ``core.http_client.HttpClient``."""

    def __init__(self) -> None:
        self.calls: list[dict[str, typing.Any]] = []

    def request(self, *args: typing.Any, **kwargs: typing.Any) -> str:
        self.calls.append({"args": args, **kwargs})
        return "ok"


def test_installs_max_retries_on_idempotent_requests() -> None:
    rec = _Recorder()
    install_default_retries(rec, max_retries=3)

    rec.request("models", method="GET")

    assert rec.calls[0]["request_options"] == {"max_retries": 3}
    # retries=0 corrects the off-by-two in the generated counter.
    assert rec.calls[0]["retries"] == 0


def test_does_not_retry_non_idempotent_requests() -> None:
    rec = _Recorder()
    install_default_retries(rec, max_retries=3)

    rec.request("models/run", method="POST")

    assert rec.calls[0]["request_options"] is None


def test_explicit_request_options_win() -> None:
    rec = _Recorder()
    install_default_retries(rec, max_retries=3)

    rec.request("models", method="GET", request_options={"max_retries": 0})
    rec.request("models", method="GET", request_options={"timeout_in_seconds": 5})

    assert rec.calls[0]["request_options"] == {"max_retries": 0}
    # Unrelated options are preserved, and the default is added alongside.
    assert rec.calls[1]["request_options"] == {"timeout_in_seconds": 5, "max_retries": 3}


def test_max_retries_zero_is_a_no_op() -> None:
    rec = _Recorder()
    install_default_retries(rec, max_retries=0)
    # No wrapper installed: request is still the bound class method, so no
    # per-instance attribute shadows it.
    assert "request" not in vars(rec)
    rec.request("models", method="GET")
    assert "request_options" not in rec.calls[0]


def _client_with_transport(
    handler: typing.Callable[[httpx.Request], httpx.Response],
    **kwargs: typing.Any,
) -> ConductorQuantum:
    return ConductorQuantum(
        token=TOKEN,
        base_url="https://example.invalid/v0/control",
        httpx_client=httpx.Client(transport=httpx.MockTransport(handler)),
        **kwargs,
    )


def test_transient_500_is_retried_end_to_end(monkeypatch: pytest.MonkeyPatch) -> None:
    """Two upstream 500s are absorbed; the caller sees the eventual success."""
    monkeypatch.setattr("conductorquantum.core.http_client.time.sleep", lambda _: None)
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        if attempts <= 2:
            return httpx.Response(500, text="Internal Server Error")
        return httpx.Response(200, json=[])

    client = _client_with_transport(handler)
    assert client.control.models.list(limit=1) == []
    assert attempts == 3


def test_gives_up_after_max_retries(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("conductorquantum.core.http_client.time.sleep", lambda _: None)
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        return httpx.Response(500, text="Internal Server Error")

    from conductorquantum.core.api_error import ApiError

    client = _client_with_transport(handler)
    with pytest.raises(ApiError):
        client.control.models.list(limit=1)

    # 1 initial attempt + DEFAULT_MAX_RETRIES retries.
    assert attempts == DEFAULT_MAX_RETRIES + 1


def test_401_is_not_retried(monkeypatch: pytest.MonkeyPatch) -> None:
    """A 401 is not in the retryable set, so it fails fast.

    The upstream 'Unable to verify API token' flake is a masked infrastructure
    error and is *not* covered by client-side retries; it needs a server-side
    fix. This test pins the current behaviour so that stays visible.
    """
    monkeypatch.setattr("conductorquantum.core.http_client.time.sleep", lambda _: None)
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        return httpx.Response(401, json={"detail": "Unable to verify API token."})

    from conductorquantum.core.api_error import ApiError

    client = _client_with_transport(handler)
    with pytest.raises(ApiError):
        client.control.models.list(limit=1)

    assert attempts == 1


def test_retries_can_be_disabled_per_client() -> None:
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        return httpx.Response(500, text="Internal Server Error")

    from conductorquantum.core.api_error import ApiError

    client = _client_with_transport(handler, max_retries=0)
    with pytest.raises(ApiError):
        client.control.models.list(limit=1)

    assert attempts == 1
