"""Integration tests for the Control API agents and Ising model endpoints.

These tests run against the live API at https://api.conductorquantum.com/v0/control
and require a valid API key set via the CONTROL_API_TOKEN or CONDUCTOR_QUANTUM_API_KEY
environment variable.

Usage:
    CONTROL_API_TOKEN=<key> pytest tests/custom/test_agents_integration.py -v
"""

from __future__ import annotations

import base64
import os
from pathlib import Path
from typing import NoReturn

import httpx
import numpy as np
import pytest

from conductorquantum import (
    AgentPublic,
    AsyncConductorQuantum,
    ConductorQuantum,
    ModelResultPublic,
)
from conductorquantum.core.api_error import ApiError
from conductorquantum.core.request_options import RequestOptions

_FIXTURES_DIR = Path(__file__).parent / "fixtures"
_QCALEVAL_IMG = _FIXTURES_DIR / "qcaleval_drag.png"
# Read lazily so pytest collection doesn't fail if the fixture is missing
# (e.g. shallow clone, future refactor). Tests that need the image skip below.
_QCALEVAL_B64 = base64.b64encode(_QCALEVAL_IMG.read_bytes()).decode() if _QCALEVAL_IMG.exists() else ""

ISING_CALIBRATION_BODY = {
    "image_base64": _QCALEVAL_B64,
    "prompt": "Describe this calibration plot.",
    "max_tokens": 64,
}

# VLM cold-start can exceed 5 minutes; skip rather than block CI.
CALIBRATION_TIMEOUT_SECONDS = 10

# Minimal syndrome tensor: batch=1, channels=4, T=3, D=3, D=3
ISING_DECODING_SYNDROME = np.zeros((1, 4, 3, 3, 3), dtype=np.float32)

_skip_no_key = pytest.mark.skipif(
    not (os.environ.get("CONTROL_API_TOKEN") or os.environ.get("CONDUCTOR_QUANTUM_API_KEY")),
    reason="Set CONTROL_API_TOKEN or CONDUCTOR_QUANTUM_API_KEY",
)

_skip_no_qcaleval_fixture = pytest.mark.skipif(
    not _QCALEVAL_IMG.exists(),
    reason=f"Calibration fixture missing: {_QCALEVAL_IMG}",
)

pytestmark = [_skip_no_key, pytest.mark.integration]


# ---------------------------------------------------------------------------
# Agents List
# ---------------------------------------------------------------------------


class TestAgentsList:
    def test_returns_list(self, client: ConductorQuantum) -> None:
        agents = client.control.agents.list()
        assert isinstance(agents, list)

    def test_each_item_is_agent_public(self, client: ConductorQuantum) -> None:
        agents = client.control.agents.list()
        if not agents:
            pytest.skip("No agents available for this token")
        for a in agents:
            assert isinstance(a, AgentPublic)
            assert a.id
            assert a.name
            assert a.description

    def test_pagination_skip_and_limit(self, client: ConductorQuantum) -> None:
        all_agents = client.control.agents.list()
        if len(all_agents) < 2:
            pytest.skip("Not enough agents to test pagination")

        first = client.control.agents.list(limit=1)
        assert len(first) == 1

        second = client.control.agents.list(skip=1, limit=1)
        assert len(second) == 1
        assert first[0].id != second[0].id


# ---------------------------------------------------------------------------
# Async Client — Agents List
# ---------------------------------------------------------------------------


class TestAsyncAgentsList:
    async def test_list(self, async_client: AsyncConductorQuantum) -> None:
        agents = await async_client.control.agents.list()
        assert isinstance(agents, list)
        for a in agents:
            assert isinstance(a, AgentPublic)


# ---------------------------------------------------------------------------
# Control namespace
# ---------------------------------------------------------------------------


class TestControlAgentsNamespace:
    def test_control_agents_list(self, client: ConductorQuantum) -> None:
        agents = client.control.agents.list()
        assert isinstance(agents, list)


# ---------------------------------------------------------------------------
# Agents Run — Ising Calibration (VLM, long cold-start)
# ---------------------------------------------------------------------------


def _calibration_skip_msg(exc: BaseException) -> str:
    return f"ising-calibration-v1 unavailable (cold/transient): {type(exc).__name__}"


# Narrow set of exceptions that indicate transient VLM cold-start or
# infrastructure unavailability. Anything else (AttributeError, 4xx ApiError,
# pydantic validation) is a real bug and must fail the test, not skip.
_CALIBRATION_TRANSIENT_EXCEPTIONS: tuple[type[BaseException], ...] = (
    httpx.TimeoutException,
    httpx.ConnectError,
    httpx.ReadError,
)
_CALIBRATION_TRANSIENT_STATUS_CODES = frozenset({500, 502, 503, 504})


def _skip_if_transient_calibration_error(exc: BaseException) -> NoReturn:
    """Skip the test if ``exc`` looks like cold-start / upstream 5xx; otherwise re-raise."""
    if isinstance(exc, _CALIBRATION_TRANSIENT_EXCEPTIONS):
        pytest.skip(_calibration_skip_msg(exc))
    if isinstance(exc, ApiError) and exc.status_code in _CALIBRATION_TRANSIENT_STATUS_CODES:
        pytest.skip(_calibration_skip_msg(exc))
    raise exc


@_skip_no_qcaleval_fixture
class TestIsingCalibrationAgent:
    """Ising-Calibration VLM agent tests with a short timeout.

    The VLM takes ~5 min to cold-start on Modal.  These tests use a
    10-second timeout so CI isn't blocked; if the endpoint is cold or
    returns a transient error the tests are skipped.
    """

    def test_run_returns_dict(self, client: ConductorQuantum) -> None:
        agents = client.control.agents.list()
        match = [a for a in agents if a.id == "ising-calibration-v1"]
        if not match:
            pytest.skip("ising-calibration-v1 not available")
        try:
            result = client.control.agents.run(
                "ising-calibration-v1",
                body=ISING_CALIBRATION_BODY,
                request_options=RequestOptions(timeout_in_seconds=CALIBRATION_TIMEOUT_SECONDS),
            )
        except Exception as exc:
            _skip_if_transient_calibration_error(exc)
        assert isinstance(result, dict)

    def test_response_shape(self, client: ConductorQuantum) -> None:
        agents = client.control.agents.list()
        match = [a for a in agents if a.id == "ising-calibration-v1"]
        if not match:
            pytest.skip("ising-calibration-v1 not available")
        try:
            result = client.control.agents.run(
                "ising-calibration-v1",
                body=ISING_CALIBRATION_BODY,
                request_options=RequestOptions(timeout_in_seconds=CALIBRATION_TIMEOUT_SECONDS),
            )
        except Exception as exc:
            _skip_if_transient_calibration_error(exc)
        assert "content" in result
        assert "model" in result
        assert "usage" in result


@_skip_no_qcaleval_fixture
class TestAsyncIsingCalibrationAgent:
    async def test_run_returns_dict(self, async_client: AsyncConductorQuantum) -> None:
        agents = await async_client.control.agents.list()
        match = [a for a in agents if a.id == "ising-calibration-v1"]
        if not match:
            pytest.skip("ising-calibration-v1 not available")
        try:
            result = await async_client.control.agents.run(
                "ising-calibration-v1",
                body=ISING_CALIBRATION_BODY,
                request_options=RequestOptions(timeout_in_seconds=CALIBRATION_TIMEOUT_SECONDS),
            )
        except Exception as exc:
            _skip_if_transient_calibration_error(exc)
        assert isinstance(result, dict)

    async def test_response_shape(self, async_client: AsyncConductorQuantum) -> None:
        agents = await async_client.control.agents.list()
        match = [a for a in agents if a.id == "ising-calibration-v1"]
        if not match:
            pytest.skip("ising-calibration-v1 not available")
        try:
            result = await async_client.control.agents.run(
                "ising-calibration-v1",
                body=ISING_CALIBRATION_BODY,
                request_options=RequestOptions(timeout_in_seconds=CALIBRATION_TIMEOUT_SECONDS),
            )
        except Exception as exc:
            _skip_if_transient_calibration_error(exc)
        assert "content" in result
        assert "model" in result
        assert "usage" in result


# ---------------------------------------------------------------------------
# Ising Decoding Models (CNN, fast cold-start — should respond immediately)
# ---------------------------------------------------------------------------


class TestIsingDecodingModels:
    """Ising-Decoding CNN model tests.

    The CNN is lightweight and responds within seconds even on cold start.
    """

    @pytest.mark.parametrize("model_id", ["ising-decoding-v1-fast", "ising-decoding-v1-accurate"])
    def test_execute_returns_result(self, client: ConductorQuantum, model_id: str) -> None:
        result = client.control.models.execute(model=model_id, data=ISING_DECODING_SYNDROME)
        assert isinstance(result, ModelResultPublic)
        assert result.model == model_id
        assert isinstance(result.output, dict)
        assert "logits" in result.output
        assert "variant" in result.output
        assert "batch_size" in result.output

    def test_fast_variant_returns_correct_variant(self, client: ConductorQuantum) -> None:
        result = client.control.models.execute(model="ising-decoding-v1-fast", data=ISING_DECODING_SYNDROME)
        assert result.output["variant"] == "fast"

    def test_accurate_variant_returns_correct_variant(self, client: ConductorQuantum) -> None:
        result = client.control.models.execute(model="ising-decoding-v1-accurate", data=ISING_DECODING_SYNDROME)
        assert result.output["variant"] == "accurate"


class TestAsyncIsingDecodingModels:
    @pytest.mark.parametrize("model_id", ["ising-decoding-v1-fast", "ising-decoding-v1-accurate"])
    async def test_execute_returns_result(self, async_client: AsyncConductorQuantum, model_id: str) -> None:
        result = await async_client.control.models.execute(model=model_id, data=ISING_DECODING_SYNDROME)
        assert isinstance(result, ModelResultPublic)
        assert result.model == model_id
        assert isinstance(result.output, dict)
        assert "logits" in result.output
        assert "variant" in result.output
