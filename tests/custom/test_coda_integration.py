"""Integration tests for the Coda surface on ConductorQuantum.

These tests run against the live API at https://api.conductorquantum.com/v0
and require a valid API key set via the CONDUCTOR_QUANTUM_API_KEY environment variable.

Usage:
    CONDUCTOR_QUANTUM_API_KEY=<key> pytest tests/custom/test_coda_integration.py -v
"""

from __future__ import annotations

import os

import pytest

from conductorquantum import AsyncConductorQuantum, ConductorQuantum
from conductorquantum.coda.errors import CodaAPIError

API_BASE_URL = "https://api.conductorquantum.com/v0"

_AGENTS_TERMINAL_TYPES = frozenset({"completed", "error", "cancelled"})

BELL_STATE_CODE = """\
from qiskit import QuantumCircuit

qc = QuantumCircuit(2, 2)
qc.h(0)
qc.cx(0, 1)
qc.measure([0, 1], [0, 1])
"""

_skip_no_key = pytest.mark.skipif(
    os.environ.get("CONDUCTOR_QUANTUM_API_KEY") is None,
    reason="CONDUCTOR_QUANTUM_API_KEY environment variable not set",
)

pytestmark = [_skip_no_key, pytest.mark.integration]


def _assert_agents_sse_invariants(events: list[dict]) -> None:
    """Streaming contract: JSON events with exactly one terminal event at the end."""
    assert len(events) >= 1, "Expected at least one SSE event"
    types: list[str] = []
    for ev in events:
        assert isinstance(ev, dict), f"Each event must be a dict, got {type(ev)}"
        t = ev.get("type")
        assert isinstance(t, str) and len(t) > 0, f"Each event needs non-empty str type, got {ev!r}"
        types.append(t)
    terminal_positions = [i for i, t in enumerate(types) if t in _AGENTS_TERMINAL_TYPES]
    assert len(terminal_positions) == 1, f"Expected exactly one terminal event ({_AGENTS_TERMINAL_TYPES}), types={types}"
    assert terminal_positions[0] == len(events) - 1, f"Terminal event must be last, types={types}"


# ---------------------------------------------------------------------------
# Sync client
# ---------------------------------------------------------------------------


class TestCodaHealth:
    def test_health(self, client: ConductorQuantum):
        result = client.coda.health()
        assert result.get("status") == "ok"


class TestCodaTranspile:
    def test_transpile_bell_state(self, client: ConductorQuantum):
        result = client.coda.transpile(source_code=BELL_STATE_CODE, target="cirq")
        assert result.get("success") is True
        assert result.get("source_framework") == "qiskit"
        assert result.get("target_framework") == "cirq"
        converted = result.get("converted_code", "")
        assert isinstance(converted, str) and len(converted) > 0


class TestCodaSimulate:
    def test_simulate_bell_state(self, client: ConductorQuantum):
        result = client.coda.simulate(code=BELL_STATE_CODE, shots=100)
        assert result.get("success") is True
        counts = result.get("counts")
        assert isinstance(counts, dict) and len(counts) > 0
        assert sum(counts.values()) == 100


class TestCodaOpenQASM3:
    def test_to_openqasm3(self, client: ConductorQuantum):
        result = client.coda.to_openqasm3(code=BELL_STATE_CODE)
        assert result.get("success") is True
        assert "OPENQASM" in result.get("openqasm3", "")


class TestCodaEstimateResources:
    def test_estimate_resources(self, client: ConductorQuantum):
        result = client.coda.estimate_resources(code=BELL_STATE_CODE)
        assert result.get("success") is True
        assert result.get("qubit_count") == 2


class TestCodaSplitCircuit:
    def test_split_circuit(self, client: ConductorQuantum):
        result = client.coda.split_circuit(code=BELL_STATE_CODE)
        if result.get("success") is True:
            assert result.get("original_qubit_count") == 2
        else:
            assert isinstance(result.get("error"), str)


class TestCodaQPU:
    def test_qpu_devices(self, client: ConductorQuantum):
        result = client.coda.qpu_devices()
        assert result.get("success") is True
        devices = result.get("devices", [])
        assert isinstance(devices, list) and len(devices) > 0

    def test_qpu_estimate_cost(self, client: ConductorQuantum):
        devices_resp = client.coda.qpu_devices()
        devices = devices_resp.get("devices", [])
        assert len(devices) > 0
        backend = devices[0].get("id") or devices[0]["name"]

        result = client.coda.qpu_estimate_cost(
            code=BELL_STATE_CODE,
            source_framework="qiskit",
            backend=backend,
            shots=100,
        )
        assert result.get("success") is True
        cost = result.get("estimated_cost_cents")
        assert isinstance(cost, (int, float)) and cost >= 0

    def test_qpu_status_unknown_job(self, client: ConductorQuantum):
        try:
            result = client.coda.qpu_status(job_id="nonexistent-job-id")
        except CodaAPIError:
            return
        assert result.get("success") is False


class TestCodaAgents:
    def test_agents_build_mode(self, client: ConductorQuantum):
        events = list(
            client.coda.agents(
                messages=[{"role": "user", "content": "What is a qubit?"}],
                mode="build",
                fast=True,
            )
        )
        _assert_agents_sse_invariants(events)
        assert len(events) >= 2
        assert events[-1]["type"] == "completed"

    def test_agents_learn_mode(self, client: ConductorQuantum):
        events = list(
            client.coda.agents(
                messages=[{"role": "user", "content": "Explain superposition briefly"}],
                mode="learn",
                fast=True,
            )
        )
        _assert_agents_sse_invariants(events)
        assert len(events) >= 2
        assert events[-1]["type"] == "completed"

    def test_agents_with_thread_id(self, client: ConductorQuantum):
        events = list(
            client.coda.agents(
                messages=[{"role": "user", "content": "Hi"}],
                thread_id="integration-test-thread",
                mode="build",
                fast=True,
            )
        )
        _assert_agents_sse_invariants(events)
        assert events[-1]["type"] == "completed"


# ---------------------------------------------------------------------------
# Async client
# ---------------------------------------------------------------------------


class TestAsyncCodaHealth:
    async def test_health(self, async_client: AsyncConductorQuantum):
        result = await async_client.coda.health()
        assert result.get("status") == "ok"


class TestAsyncCodaTranspile:
    async def test_transpile(self, async_client: AsyncConductorQuantum):
        result = await async_client.coda.transpile(source_code=BELL_STATE_CODE, target="cirq")
        assert result.get("success") is True


class TestAsyncCodaAgents:
    async def test_agents_build_mode(self, async_client: AsyncConductorQuantum):
        events = []
        async for event in async_client.coda.agents(
            messages=[{"role": "user", "content": "What is a qubit?"}],
            mode="build",
            fast=True,
        ):
            events.append(event)
        _assert_agents_sse_invariants(events)
        assert len(events) >= 2
        assert events[-1]["type"] == "completed"

    async def test_agents_learn_mode(self, async_client: AsyncConductorQuantum):
        events = []
        async for event in async_client.coda.agents(
            messages=[{"role": "user", "content": "Define quantum superposition in one line."}],
            mode="learn",
            fast=True,
        ):
            events.append(event)
        _assert_agents_sse_invariants(events)
        assert events[-1]["type"] == "completed"
