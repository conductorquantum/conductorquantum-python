"""Unit tests for the conductorquantum.coda client layer.

Tests use httpx.MockTransport so no external dependencies are needed beyond
httpx and pytest-asyncio (already in dev deps).
"""

from __future__ import annotations

import json

import httpx
import pytest

from conductorquantum import AsyncConductorQuantum, ConductorQuantum
from conductorquantum.coda._http import (
    DEFAULT_BASE_URL,
    api_base_url_from_env,
    build_headers,
    parse_json,
    retry_delay,
)
from conductorquantum.coda.client import AsyncCodaClient, CodaClient
from conductorquantum.coda.errors import CodaAPIError, CodaAuthError, CodaTimeoutError

BASE_URL = "http://test:9999/v0"
TOKEN = "test-token"


def _mock_transport(handler):
    """Build an httpx.MockTransport from a simple handler function."""
    return httpx.MockTransport(handler)


def _json_response(body: dict, status: int = 200) -> httpx.Response:
    return httpx.Response(status, json=body)


def _sse_response(events: list[dict]) -> httpx.Response:
    lines = [f"data: {json.dumps(ev)}\n\n" for ev in events]
    body = "".join(lines)
    return httpx.Response(200, content=body, headers={"content-type": "text/event-stream"})


# ---------------------------------------------------------------------------
# Root client wiring
# ---------------------------------------------------------------------------


class TestRootClientCoda:
    def test_sync_client_exposes_coda(self):
        client = ConductorQuantum(token=TOKEN)
        assert hasattr(client, "coda")
        assert isinstance(client.coda, CodaClient)

    def test_async_client_exposes_coda(self):
        client = AsyncConductorQuantum(token=TOKEN)
        assert hasattr(client, "coda")
        assert isinstance(client.coda, AsyncCodaClient)

    def test_coda_uses_same_base_url(self):
        client = ConductorQuantum(token=TOKEN, base_url=BASE_URL)
        assert str(client.coda._client.base_url).rstrip("/") == BASE_URL

    def test_coda_uses_callable_token(self):
        client = ConductorQuantum(token=lambda: "dynamic-token")
        assert "dynamic-token" in client.coda._client.headers["authorization"]


# ---------------------------------------------------------------------------
# api_base_url_from_env
# ---------------------------------------------------------------------------


class TestApiBaseUrlFromEnv:
    def test_defaults_to_production(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.delenv("CODA_API_BASE_URL", raising=False)
        monkeypatch.delenv("CODA_BASE_URL", raising=False)
        assert api_base_url_from_env() == DEFAULT_BASE_URL

    def test_coda_api_base_url_wins(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setenv("CODA_API_BASE_URL", "https://custom.example.com/v0")
        monkeypatch.setenv("CODA_BASE_URL", "http://ignored")
        assert api_base_url_from_env() == "https://custom.example.com/v0"

    def test_coda_base_url_appends_v0(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.delenv("CODA_API_BASE_URL", raising=False)
        monkeypatch.setenv("CODA_BASE_URL", "http://localhost:9999")
        assert api_base_url_from_env() == "http://localhost:9999/v0"

    def test_coda_base_url_with_v0_unchanged(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.delenv("CODA_API_BASE_URL", raising=False)
        monkeypatch.setenv("CODA_BASE_URL", "http://localhost:9999/v0")
        assert api_base_url_from_env() == "http://localhost:9999/v0"


# ---------------------------------------------------------------------------
# build_headers
# ---------------------------------------------------------------------------


class TestBuildHeaders:
    def test_includes_bearer_token(self):
        h = build_headers("my-token", "1.2.3")
        assert h["Authorization"] == "Bearer my-token"

    def test_includes_user_agent_with_version(self):
        h = build_headers("tok", "1.2.3")
        assert h["User-Agent"] == "conductorquantum-python/1.2.3"


# ---------------------------------------------------------------------------
# Error hierarchy
# ---------------------------------------------------------------------------


class TestErrors:
    def test_coda_api_error(self):
        err = CodaAPIError(500, "boom", {"detail": "boom"})
        assert err.status_code == 500
        assert err.detail == "boom"
        assert "[500]" in str(err)

    def test_coda_auth_error_is_api_error(self):
        err = CodaAuthError(401, "bad token")
        assert isinstance(err, CodaAPIError)
        assert err.status_code == 401

    def test_coda_timeout_error(self):
        err = CodaTimeoutError("timed out")
        assert "timed out" in str(err)


# ---------------------------------------------------------------------------
# parse_json / error handling
# ---------------------------------------------------------------------------


class TestParseJson:
    def test_success(self):
        resp = httpx.Response(200, json={"status": "ok"}, request=httpx.Request("GET", BASE_URL))
        assert parse_json(resp) == {"status": "ok"}

    def test_401_raises_auth_error(self):
        resp = httpx.Response(401, json={"detail": "Invalid token"}, request=httpx.Request("GET", BASE_URL))
        with pytest.raises(CodaAuthError) as exc_info:
            parse_json(resp)
        assert exc_info.value.status_code == 401

    def test_500_raises_api_error(self):
        resp = httpx.Response(500, json={"detail": "Internal error"}, request=httpx.Request("GET", BASE_URL))
        with pytest.raises(CodaAPIError) as exc_info:
            parse_json(resp)
        assert exc_info.value.status_code == 500

    def test_empty_body_raises_with_hint(self):
        resp = httpx.Response(200, content=b"", request=httpx.Request("GET", BASE_URL))
        with pytest.raises(CodaAPIError) as exc_info:
            parse_json(resp)
        assert "CODA_API_BASE_URL" in exc_info.value.detail

    def test_html_body_raises_with_hint(self):
        resp = httpx.Response(200, content=b"<html>login</html>", request=httpx.Request("GET", BASE_URL))
        with pytest.raises(CodaAPIError) as exc_info:
            parse_json(resp)
        assert "HTML" in exc_info.value.detail

    def test_redirect_to_login_includes_hint(self):
        resp = httpx.Response(
            307,
            content=b"/login",
            headers={"location": "http://localhost:3000/login"},
            request=httpx.Request("GET", BASE_URL),
        )
        with pytest.raises(CodaAPIError) as exc_info:
            parse_json(resp)
        assert "CODA_API_BASE_URL" in exc_info.value.detail


# ---------------------------------------------------------------------------
# retry_delay
# ---------------------------------------------------------------------------


class TestRetryDelay:
    def test_exponential_backoff(self):
        assert retry_delay(0) == 0.5
        assert retry_delay(1) == 1.0
        assert retry_delay(2) == 2.0

    def test_capped_at_10(self):
        assert retry_delay(10) == 10.0


# ---------------------------------------------------------------------------
# Sync CodaClient
# ---------------------------------------------------------------------------


class TestCodaClientHealth:
    def test_health(self):
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/v0/health"
            return _json_response({"status": "ok"})

        client = CodaClient(token=TOKEN, base_url=BASE_URL, sdk_version="0.0.0")
        client._client = httpx.Client(base_url=BASE_URL, transport=_mock_transport(handler))
        assert client.health() == {"status": "ok"}


class TestCodaClientTranspile:
    def test_transpile_sends_correct_body(self):
        def handler(request: httpx.Request) -> httpx.Response:
            body = json.loads(request.content)
            assert body == {"source_code": "qc = QuantumCircuit(2)", "target": "cirq"}
            return _json_response({"success": True, "converted_code": "cirq_code"})

        client = CodaClient(token=TOKEN, base_url=BASE_URL, sdk_version="0.0.0")
        client._client = httpx.Client(base_url=BASE_URL, transport=_mock_transport(handler))
        result = client.transpile(source_code="qc = QuantumCircuit(2)", target="cirq")
        assert result["success"] is True


class TestCodaClientSimulate:
    def test_simulate_defaults(self):
        def handler(request: httpx.Request) -> httpx.Response:
            body = json.loads(request.content)
            assert body["method"] == "qasm"
            assert body["shots"] == 1024
            assert body["backend"] == "auto"
            assert "seed_simulator" not in body
            return _json_response({"success": True, "counts": {"00": 512, "11": 512}})

        client = CodaClient(token=TOKEN, base_url=BASE_URL, sdk_version="0.0.0")
        client._client = httpx.Client(base_url=BASE_URL, transport=_mock_transport(handler))
        result = client.simulate(code="code")
        assert result["success"] is True

    def test_simulate_with_seed(self):
        def handler(request: httpx.Request) -> httpx.Response:
            body = json.loads(request.content)
            assert body["seed_simulator"] == 42
            return _json_response({"success": True})

        client = CodaClient(token=TOKEN, base_url=BASE_URL, sdk_version="0.0.0")
        client._client = httpx.Client(base_url=BASE_URL, transport=_mock_transport(handler))
        client.simulate(code="code", seed_simulator=42)


class TestCodaClientCircuitTools:
    def test_to_openqasm3(self):
        def handler(request: httpx.Request) -> httpx.Response:
            return _json_response({"success": True, "openqasm3": "OPENQASM 3.0;"})

        client = CodaClient(token=TOKEN, base_url=BASE_URL, sdk_version="0.0.0")
        client._client = httpx.Client(base_url=BASE_URL, transport=_mock_transport(handler))
        result = client.to_openqasm3(code="code")
        assert result["success"] is True

    def test_estimate_resources(self):
        def handler(request: httpx.Request) -> httpx.Response:
            return _json_response({"success": True, "qubit_count": 2})

        client = CodaClient(token=TOKEN, base_url=BASE_URL, sdk_version="0.0.0")
        client._client = httpx.Client(base_url=BASE_URL, transport=_mock_transport(handler))
        result = client.estimate_resources(code="code")
        assert result["qubit_count"] == 2

    def test_split_circuit(self):
        def handler(request: httpx.Request) -> httpx.Response:
            return _json_response({"success": True})

        client = CodaClient(token=TOKEN, base_url=BASE_URL, sdk_version="0.0.0")
        client._client = httpx.Client(base_url=BASE_URL, transport=_mock_transport(handler))
        result = client.split_circuit(code="code")
        assert result["success"] is True


class TestCodaClientQPU:
    def test_qpu_submit(self):
        def handler(request: httpx.Request) -> httpx.Response:
            body = json.loads(request.content)
            assert body["code"] == "code"
            assert body["source_framework"] == "qiskit"
            assert body["backend"] == "iqm"
            return _json_response({"success": True, "job_id": "j-1"})

        client = CodaClient(token=TOKEN, base_url=BASE_URL, sdk_version="0.0.0")
        client._client = httpx.Client(base_url=BASE_URL, transport=_mock_transport(handler))
        result = client.qpu_submit(code="code", source_framework="qiskit", backend="iqm")
        assert result["job_id"] == "j-1"

    def test_qpu_status(self):
        def handler(request: httpx.Request) -> httpx.Response:
            body = json.loads(request.content)
            assert body == {"job_id": "j-1"}
            return _json_response({"success": True, "status": "completed"})

        client = CodaClient(token=TOKEN, base_url=BASE_URL, sdk_version="0.0.0")
        client._client = httpx.Client(base_url=BASE_URL, transport=_mock_transport(handler))
        result = client.qpu_status(job_id="j-1")
        assert result["status"] == "completed"

    def test_qpu_devices(self):
        def handler(request: httpx.Request) -> httpx.Response:
            return _json_response({"success": True, "devices": [{"name": "iqm"}]})

        client = CodaClient(token=TOKEN, base_url=BASE_URL, sdk_version="0.0.0")
        client._client = httpx.Client(base_url=BASE_URL, transport=_mock_transport(handler))
        result = client.qpu_devices()
        assert len(result["devices"]) == 1

    def test_qpu_estimate_cost(self):
        def handler(request: httpx.Request) -> httpx.Response:
            return _json_response({"success": True, "estimated_cost_cents": 50})

        client = CodaClient(token=TOKEN, base_url=BASE_URL, sdk_version="0.0.0")
        client._client = httpx.Client(base_url=BASE_URL, transport=_mock_transport(handler))
        result = client.qpu_estimate_cost(code="code", source_framework="qiskit", backend="iqm")
        assert result["estimated_cost_cents"] == 50


class TestCodaClientAgents:
    def test_agents_yields_events(self):
        events = [{"type": "token", "content": "Hello"}, {"type": "completed"}]

        def handler(request: httpx.Request) -> httpx.Response:
            body = json.loads(request.content)
            assert body["messages"] == [{"role": "user", "content": "hi"}]
            assert body["mode"] == "build"
            assert body["fast"] is False
            return _sse_response(events)

        client = CodaClient(token=TOKEN, base_url=BASE_URL, sdk_version="0.0.0")
        client._client = httpx.Client(base_url=BASE_URL, transport=_mock_transport(handler))
        collected = list(client.agents(messages=[{"role": "user", "content": "hi"}]))

        assert len(collected) == 2
        assert collected[0]["type"] == "token"
        assert collected[1]["type"] == "completed"

    def test_agents_sends_thread_id(self):
        def handler(request: httpx.Request) -> httpx.Response:
            body = json.loads(request.content)
            assert body["thread_id"] == "t-1"
            assert body["fast"] is True
            assert body["mode"] == "learn"
            return _sse_response([{"type": "completed"}])

        client = CodaClient(token=TOKEN, base_url=BASE_URL, sdk_version="0.0.0")
        client._client = httpx.Client(base_url=BASE_URL, transport=_mock_transport(handler))
        list(
            client.agents(
                messages=[{"role": "user", "content": "test"}],
                thread_id="t-1",
                fast=True,
                mode="learn",
            )
        )

    def test_agents_omits_thread_id_when_none(self):
        def handler(request: httpx.Request) -> httpx.Response:
            body = json.loads(request.content)
            assert "thread_id" not in body
            return _sse_response([{"type": "completed"}])

        client = CodaClient(token=TOKEN, base_url=BASE_URL, sdk_version="0.0.0")
        client._client = httpx.Client(base_url=BASE_URL, transport=_mock_transport(handler))
        list(client.agents(messages=[{"role": "user", "content": "hi"}]))

    def test_agents_skips_non_data_lines(self):
        def handler(request: httpx.Request) -> httpx.Response:
            body = ": keepalive\n\ndata: " + json.dumps({"type": "completed"}) + "\n\n"
            return httpx.Response(200, content=body, headers={"content-type": "text/event-stream"})

        client = CodaClient(token=TOKEN, base_url=BASE_URL, sdk_version="0.0.0")
        client._client = httpx.Client(base_url=BASE_URL, transport=_mock_transport(handler))
        collected = list(client.agents(messages=[{"role": "user", "content": "hi"}]))
        assert len(collected) == 1
        assert collected[0]["type"] == "completed"

    def test_agents_401_raises_auth_error(self):
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(401, json={"detail": "Invalid token"})

        client = CodaClient(token=TOKEN, base_url=BASE_URL, sdk_version="0.0.0")
        client._client = httpx.Client(base_url=BASE_URL, transport=_mock_transport(handler))
        with pytest.raises(CodaAuthError):
            list(client.agents(messages=[{"role": "user", "content": "hi"}]))

    def test_agents_307_raises_api_error(self):
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(307, headers={"location": "/login"}, content=b"/login")

        client = CodaClient(token=TOKEN, base_url=BASE_URL, sdk_version="0.0.0")
        client._client = httpx.Client(base_url=BASE_URL, transport=_mock_transport(handler))
        with pytest.raises(CodaAPIError) as exc_info:
            list(client.agents(messages=[{"role": "user", "content": "hi"}]))
        assert exc_info.value.status_code == 307
        assert "CODA_API_BASE_URL" in exc_info.value.detail


# ---------------------------------------------------------------------------
# QPU optional fields
# ---------------------------------------------------------------------------


class TestCodaClientQpuOptionalFields:
    def test_qpu_submit_sends_optional_fields(self):
        def handler(request: httpx.Request) -> httpx.Response:
            body = json.loads(request.content)
            assert body["accept_overage"] is True
            assert body["braket_execution_mode_hint"] == "program_set"
            assert body["shots"] == 200
            return _json_response({"success": True, "job_id": "j-1"})

        client = CodaClient(token=TOKEN, base_url=BASE_URL, sdk_version="0.0.0")
        client._client = httpx.Client(base_url=BASE_URL, transport=_mock_transport(handler))
        client.qpu_submit(
            code="code",
            source_framework="qiskit",
            backend="ionq",
            shots=200,
            accept_overage=True,
            braket_execution_mode_hint="program_set",
        )

    def test_qpu_estimate_cost_sends_optional_fields(self):
        def handler(request: httpx.Request) -> httpx.Response:
            body = json.loads(request.content)
            assert body["braket_execution_mode_hint"] == "run_batch"
            assert body["shots"] == 500
            return _json_response({"success": True, "estimated_cost_cents": 100})

        client = CodaClient(token=TOKEN, base_url=BASE_URL, sdk_version="0.0.0")
        client._client = httpx.Client(base_url=BASE_URL, transport=_mock_transport(handler))
        client.qpu_estimate_cost(
            code="code",
            source_framework="qiskit",
            backend="ionq",
            shots=500,
            braket_execution_mode_hint="run_batch",
        )

    def test_qpu_status_sends_job_id(self):
        def handler(request: httpx.Request) -> httpx.Response:
            body = json.loads(request.content)
            assert body == {"job_id": "j-abc"}
            return _json_response({"success": True, "status": "running"})

        client = CodaClient(token=TOKEN, base_url=BASE_URL, sdk_version="0.0.0")
        client._client = httpx.Client(base_url=BASE_URL, transport=_mock_transport(handler))
        client.qpu_status(job_id="j-abc")


# ---------------------------------------------------------------------------
# Retry behavior
# ---------------------------------------------------------------------------


class TestCodaClientRetry:
    def test_retries_on_429(self):
        call_count = 0

        def handler(request: httpx.Request) -> httpx.Response:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return httpx.Response(429, json={"detail": "Rate limited"})
            return _json_response({"status": "ok"})

        client = CodaClient(token=TOKEN, base_url=BASE_URL, sdk_version="0.0.0")
        client._client = httpx.Client(base_url=BASE_URL, transport=_mock_transport(handler))
        result = client.health()
        assert result == {"status": "ok"}
        assert call_count == 2

    def test_retries_on_500(self):
        call_count = 0

        def handler(request: httpx.Request) -> httpx.Response:
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                return httpx.Response(500, json={"detail": "Error"})
            return _json_response({"status": "ok"})

        client = CodaClient(token=TOKEN, base_url=BASE_URL, sdk_version="0.0.0")
        client._client = httpx.Client(base_url=BASE_URL, transport=_mock_transport(handler))
        result = client.health()
        assert result == {"status": "ok"}
        assert call_count == 3


class TestCodaClientTimeout:
    def test_timeout_raises_coda_timeout_error(self):
        def handler(request: httpx.Request) -> httpx.Response:
            raise httpx.ReadTimeout("timed out")

        client = CodaClient(token=TOKEN, base_url=BASE_URL, sdk_version="0.0.0")
        client._client = httpx.Client(base_url=BASE_URL, transport=_mock_transport(handler))
        with pytest.raises(CodaTimeoutError, match="timed out"):
            client.health()


# ---------------------------------------------------------------------------
# Async CodaClient
# ---------------------------------------------------------------------------


class TestAsyncCodaClientHealth:
    async def test_health(self):
        async def handler(request: httpx.Request) -> httpx.Response:
            return _json_response({"status": "ok"})

        client = AsyncCodaClient(token=TOKEN, base_url=BASE_URL, sdk_version="0.0.0")
        client._client = httpx.AsyncClient(base_url=BASE_URL, transport=httpx.MockTransport(handler))
        result = await client.health()
        assert result == {"status": "ok"}


class TestAsyncCodaClientTranspile:
    async def test_transpile(self):
        async def handler(request: httpx.Request) -> httpx.Response:
            return _json_response({"success": True, "converted_code": "cirq_code"})

        client = AsyncCodaClient(token=TOKEN, base_url=BASE_URL, sdk_version="0.0.0")
        client._client = httpx.AsyncClient(base_url=BASE_URL, transport=httpx.MockTransport(handler))
        result = await client.transpile(source_code="code", target="cirq")
        assert result["success"] is True


class TestAsyncCodaClientAgents:
    async def test_agents_yields_events(self):
        events = [{"type": "token", "content": "Hello"}, {"type": "completed"}]

        async def handler(request: httpx.Request) -> httpx.Response:
            return _sse_response(events)

        client = AsyncCodaClient(token=TOKEN, base_url=BASE_URL, sdk_version="0.0.0")
        client._client = httpx.AsyncClient(base_url=BASE_URL, transport=httpx.MockTransport(handler))
        collected = [ev async for ev in client.agents(messages=[{"role": "user", "content": "hi"}])]

        assert len(collected) == 2
        assert collected[0]["type"] == "token"
        assert collected[1]["type"] == "completed"

    async def test_agents_sends_correct_body(self):
        async def handler(request: httpx.Request) -> httpx.Response:
            body = json.loads(request.content)
            assert body["thread_id"] == "t-2"
            assert body["fast"] is True
            assert body["mode"] == "learn"
            return _sse_response([{"type": "completed"}])

        client = AsyncCodaClient(token=TOKEN, base_url=BASE_URL, sdk_version="0.0.0")
        client._client = httpx.AsyncClient(base_url=BASE_URL, transport=httpx.MockTransport(handler))
        _ = [
            ev
            async for ev in client.agents(
                messages=[{"role": "user", "content": "test"}],
                thread_id="t-2",
                fast=True,
                mode="learn",
            )
        ]

    async def test_agents_skips_keepalive_lines(self):
        async def handler(request: httpx.Request) -> httpx.Response:
            body = ": keepalive\n\ndata: " + json.dumps({"type": "completed"}) + "\n\n"
            return httpx.Response(200, content=body, headers={"content-type": "text/event-stream"})

        client = AsyncCodaClient(token=TOKEN, base_url=BASE_URL, sdk_version="0.0.0")
        client._client = httpx.AsyncClient(base_url=BASE_URL, transport=httpx.MockTransport(handler))
        collected = [ev async for ev in client.agents(messages=[{"role": "user", "content": "hi"}])]
        assert len(collected) == 1

    async def test_agents_401_raises_auth_error(self):
        async def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(401, json={"detail": "Invalid token"})

        client = AsyncCodaClient(token=TOKEN, base_url=BASE_URL, sdk_version="0.0.0")
        client._client = httpx.AsyncClient(base_url=BASE_URL, transport=httpx.MockTransport(handler))
        with pytest.raises(CodaAuthError):
            _ = [ev async for ev in client.agents(messages=[{"role": "user", "content": "hi"}])]

    async def test_agents_307_raises_api_error(self):
        async def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(307, headers={"location": "/login"}, content=b"/login")

        client = AsyncCodaClient(token=TOKEN, base_url=BASE_URL, sdk_version="0.0.0")
        client._client = httpx.AsyncClient(base_url=BASE_URL, transport=httpx.MockTransport(handler))
        with pytest.raises(CodaAPIError) as exc_info:
            _ = [ev async for ev in client.agents(messages=[{"role": "user", "content": "hi"}])]
        assert exc_info.value.status_code == 307
        assert "CODA_API_BASE_URL" in exc_info.value.detail


class TestAsyncCodaClientRetry:
    async def test_retries_on_503(self):
        call_count = 0

        async def handler(request: httpx.Request) -> httpx.Response:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return httpx.Response(503, json={"detail": "Unavailable"})
            return _json_response({"status": "ok"})

        client = AsyncCodaClient(token=TOKEN, base_url=BASE_URL, sdk_version="0.0.0")
        client._client = httpx.AsyncClient(base_url=BASE_URL, transport=httpx.MockTransport(handler))
        result = await client.health()
        assert result == {"status": "ok"}
        assert call_count == 2


class TestAsyncCodaClientTimeout:
    async def test_timeout_raises_coda_timeout_error(self):
        async def handler(request: httpx.Request) -> httpx.Response:
            raise httpx.ReadTimeout("timed out")

        client = AsyncCodaClient(token=TOKEN, base_url=BASE_URL, sdk_version="0.0.0")
        client._client = httpx.AsyncClient(base_url=BASE_URL, transport=httpx.MockTransport(handler))
        with pytest.raises(CodaTimeoutError, match="timed out"):
            await client.health()


# ---------------------------------------------------------------------------
# Error handling (sync client)
# ---------------------------------------------------------------------------


class TestCodaClientErrors:
    def test_401_raises_auth_error(self):
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(401, json={"detail": "Invalid token"})

        client = CodaClient(token=TOKEN, base_url=BASE_URL, sdk_version="0.0.0")
        client._client = httpx.Client(base_url=BASE_URL, transport=_mock_transport(handler))
        with pytest.raises(CodaAuthError) as exc_info:
            client.health()
        assert exc_info.value.status_code == 401

    def test_500_raises_api_error(self):
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(500, json={"detail": "Internal error"})

        client = CodaClient(token=TOKEN, base_url=BASE_URL, sdk_version="0.0.0")
        client._client = httpx.Client(base_url=BASE_URL, transport=_mock_transport(handler))
        with pytest.raises(CodaAPIError) as exc_info:
            client.health()
        assert exc_info.value.status_code == 500
