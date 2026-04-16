"""Integration tests for the Coda surface on ConductorQuantum.

These tests run against the live Coda API (Vercel-backed) at
https://api.conductorquantum.com/v0 and require a valid Coda API token.

Usage:
    CODA_API_TOKEN=<key> pytest tests/custom/test_coda_integration.py -v
"""

from __future__ import annotations

import contextlib
import os
import warnings

import pytest
from conductorquantum import AsyncConductorQuantum, ConductorQuantum
from conductorquantum.coda.errors import CodaAPIError

_AGENTS_TERMINAL_TYPES = frozenset({"completed", "error", "cancelled"})


@contextlib.contextmanager
def skip_if_service_unavailable():
    """Skip the test when the backend returns 503 (service not configured)."""
    try:
        yield
    except CodaAPIError as exc:
        if exc.status_code == 503:
            pytest.skip(f"Agents service unavailable: {exc}")
        raise


@contextlib.asynccontextmanager
async def async_skip_if_service_unavailable():
    """Async variant — skip the test when the backend returns 503."""
    try:
        yield
    except CodaAPIError as exc:
        if exc.status_code == 503:
            pytest.skip(f"Agents service unavailable: {exc}")
        raise

BELL_STATE_CODE = """\
from qiskit import QuantumCircuit

qc = QuantumCircuit(2, 2)
qc.h(0)
qc.cx(0, 1)
qc.measure([0, 1], [0, 1])
"""

_skip_no_key = pytest.mark.skipif(
    not (os.environ.get("CODA_API_TOKEN") or os.environ.get("CONDUCTOR_QUANTUM_API_KEY")),
    reason="Set CODA_API_TOKEN or CONDUCTOR_QUANTUM_API_KEY",
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
    assert (
        len(terminal_positions) == 1
    ), f"Expected exactly one terminal event ({_AGENTS_TERMINAL_TYPES}), types={types}"
    assert terminal_positions[0] == len(events) - 1, f"Terminal event must be last, types={types}"


# ---------------------------------------------------------------------------
# Sync client
# ---------------------------------------------------------------------------


class TestCodaHealth:
    def test_health(self, coda_client: ConductorQuantum):
        result = coda_client.coda.health()
        assert result.get("status") == "ok"


class TestCodaTranspile:
    def test_transpile_bell_state(self, coda_client: ConductorQuantum):
        result = coda_client.coda.transpile(source_code=BELL_STATE_CODE, target="cirq")
        assert result.get("success") is True
        assert result.get("source_framework") == "qiskit"
        assert result.get("target_framework") == "cirq"
        converted = result.get("converted_code", "")
        assert isinstance(converted, str) and len(converted) > 0


class TestCodaSimulate:
    def test_simulate_bell_state(self, coda_client: ConductorQuantum):
        result = coda_client.coda.simulate(code=BELL_STATE_CODE, shots=100)
        assert result.get("success") is True
        counts = result.get("counts")
        assert isinstance(counts, dict) and len(counts) > 0
        assert sum(counts.values()) == 100


class TestCodaOpenQASM3:
    def test_to_openqasm3(self, coda_client: ConductorQuantum):
        result = coda_client.coda.to_openqasm3(code=BELL_STATE_CODE)
        assert result.get("success") is True
        assert "OPENQASM" in result.get("openqasm3", "")


class TestCodaEstimateResources:
    def test_estimate_resources(self, coda_client: ConductorQuantum):
        result = coda_client.coda.estimate_resources(code=BELL_STATE_CODE)
        assert result.get("success") is True
        assert result.get("qubit_count") == 2


class TestCodaSplitCircuit:
    def test_split_circuit(self, coda_client: ConductorQuantum):
        result = coda_client.coda.split_circuit(code=BELL_STATE_CODE)
        if result.get("success") is True:
            assert result.get("original_qubit_count") == 2
        else:
            assert isinstance(result.get("error"), str)


class TestCodaQPU:
    def test_qpu_devices(self, coda_client: ConductorQuantum):
        result = coda_client.coda.qpu_devices()
        assert result.get("success") is True
        devices = result.get("devices", [])
        assert isinstance(devices, list) and len(devices) > 0

    def test_qpu_estimate_cost(self, coda_client: ConductorQuantum):
        devices_resp = coda_client.coda.qpu_devices()
        devices = devices_resp.get("devices", [])
        assert len(devices) > 0
        backend = devices[0].get("id") or devices[0]["name"]

        result = coda_client.coda.qpu_estimate_cost(
            code=BELL_STATE_CODE,
            source_framework="qiskit",
            backend=backend,
            shots=100,
        )
        assert result.get("success") is True
        cost = result.get("estimated_cost_cents")
        assert isinstance(cost, (int, float)) and cost >= 0

    def test_qpu_status_unknown_job(self, coda_client: ConductorQuantum):
        try:
            result = coda_client.coda.qpu_status(job_id="nonexistent-job-id")
        except CodaAPIError:
            return
        assert result.get("success") is False


class TestCodaAgents:
    def test_agents_build_mode(self, coda_client: ConductorQuantum):
        with skip_if_service_unavailable():
            events = list(
                coda_client.coda.agents(
                    messages=[{"role": "user", "content": "What is a qubit?"}],
                    mode="build",
                    fast=True,
                )
            )
        _assert_agents_sse_invariants(events)
        assert len(events) >= 2
        assert events[-1]["type"] == "completed"

    def test_agents_learn_mode(self, coda_client: ConductorQuantum):
        with skip_if_service_unavailable():
            events = list(
                coda_client.coda.agents(
                    messages=[{"role": "user", "content": "Explain superposition briefly"}],
                    mode="learn",
                    fast=True,
                )
            )
        _assert_agents_sse_invariants(events)
        assert len(events) >= 2
        assert events[-1]["type"] == "completed"

    def test_agents_with_thread_id(self, coda_client: ConductorQuantum):
        with skip_if_service_unavailable():
            events = list(
                coda_client.coda.agents(
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


# ---------------------------------------------------------------------------
# New namespaced API — sync (coda.tools.*, coda.qpus.*, coda.agents.*)
# ---------------------------------------------------------------------------


class TestCodaToolsTranspile:
    def test_transpile(self, coda_client: ConductorQuantum):
        result = coda_client.coda.tools.transpile(source_code=BELL_STATE_CODE, target="cirq")
        assert result.get("success") is True
        assert result.get("source_framework") == "qiskit"
        assert result.get("target_framework") == "cirq"
        converted = result.get("converted_code", "")
        assert isinstance(converted, str) and len(converted) > 0


class TestCodaToolsSimulate:
    def test_simulate(self, coda_client: ConductorQuantum):
        result = coda_client.coda.tools.simulate(code=BELL_STATE_CODE, shots=100)
        assert result.get("success") is True
        counts = result.get("counts")
        assert isinstance(counts, dict) and len(counts) > 0
        assert sum(counts.values()) == 100


class TestCodaToolsOpenQASM3:
    def test_to_openqasm3(self, coda_client: ConductorQuantum):
        result = coda_client.coda.tools.to_openqasm3(code=BELL_STATE_CODE)
        assert result.get("success") is True
        assert "OPENQASM" in result.get("openqasm3", "")


class TestCodaToolsEstimateResources:
    def test_estimate_resources(self, coda_client: ConductorQuantum):
        result = coda_client.coda.tools.estimate_resources(code=BELL_STATE_CODE)
        assert result.get("success") is True
        assert result.get("qubit_count") == 2


class TestCodaToolsSplitCircuit:
    def test_split_circuit(self, coda_client: ConductorQuantum):
        result = coda_client.coda.tools.split_circuit(code=BELL_STATE_CODE)
        if result.get("success") is True:
            assert result.get("original_qubit_count") == 2
        else:
            assert isinstance(result.get("error"), str)


class TestCodaQPUsList:
    def test_qpus_list(self, coda_client: ConductorQuantum):
        result = coda_client.coda.qpus.list()
        assert result.get("success") is True
        devices = result.get("devices", [])
        assert isinstance(devices, list) and len(devices) > 0


class TestCodaQPUsEstimateCost:
    def test_estimate_cost(self, coda_client: ConductorQuantum):
        devices_resp = coda_client.coda.qpus.list()
        devices = devices_resp.get("devices", [])
        assert len(devices) > 0
        backend = devices[0].get("id") or devices[0]["name"]

        result = coda_client.coda.qpus.estimate_cost(
            code=BELL_STATE_CODE,
            source_framework="qiskit",
            backend=backend,
            shots=100,
        )
        assert result.get("success") is True
        cost = result.get("estimated_cost_cents")
        assert isinstance(cost, (int, float)) and cost >= 0


class TestCodaQPUsStatus:
    def test_status_unknown_job(self, coda_client: ConductorQuantum):
        try:
            result = coda_client.coda.qpus.status(job_id="nonexistent-job-id")
        except CodaAPIError:
            return
        assert result.get("success") is False


class TestCodaAgentsRun:
    def test_agents_run_build(self, coda_client: ConductorQuantum):
        with skip_if_service_unavailable():
            events = list(
                coda_client.coda.agents.run(
                    messages=[{"role": "user", "content": "What is a qubit?"}],
                    mode="build",
                    fast=True,
                )
            )
        _assert_agents_sse_invariants(events)
        assert len(events) >= 2
        assert events[-1]["type"] == "completed"


class TestCodaAgentsList:
    def test_agents_list(self, coda_client: ConductorQuantum):
        with skip_if_service_unavailable():
            result = coda_client.coda.agents.list()
        assert isinstance(result, dict)
        assert "agents" in result or "modes" in result


# ---------------------------------------------------------------------------
# Legacy shortcut parity — verify deprecated and new methods return matching data
# ---------------------------------------------------------------------------


class TestLegacyShortcutParity:
    def test_transpile_parity(self, coda_client: ConductorQuantum):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            legacy = coda_client.coda.transpile(source_code=BELL_STATE_CODE, target="cirq")
        new = coda_client.coda.tools.transpile(source_code=BELL_STATE_CODE, target="cirq")

        assert legacy.get("success") == new.get("success")
        assert legacy.get("source_framework") == new.get("source_framework")
        assert legacy.get("target_framework") == new.get("target_framework")

    def test_simulate_parity(self, coda_client: ConductorQuantum):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            legacy = coda_client.coda.simulate(code=BELL_STATE_CODE, shots=100)
        new = coda_client.coda.tools.simulate(code=BELL_STATE_CODE, shots=100)

        assert legacy.get("success") == new.get("success")
        assert legacy.get("method") == new.get("method")

    def test_estimate_resources_parity(self, coda_client: ConductorQuantum):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            legacy = coda_client.coda.estimate_resources(code=BELL_STATE_CODE)
        new = coda_client.coda.tools.estimate_resources(code=BELL_STATE_CODE)

        assert legacy.get("success") == new.get("success")
        assert legacy.get("qubit_count") == new.get("qubit_count")

    def test_qpu_devices_parity(self, coda_client: ConductorQuantum):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            legacy = coda_client.coda.qpu_devices()
        new = coda_client.coda.qpus.list()

        assert legacy.get("success") == new.get("success")
        legacy_ids = {d.get("id") or d["name"] for d in legacy.get("devices", [])}
        new_ids = {d.get("id") or d["name"] for d in new.get("devices", [])}
        assert legacy_ids == new_ids


# ---------------------------------------------------------------------------
# Async client
# ---------------------------------------------------------------------------


class TestAsyncCodaHealth:
    async def test_health(self, async_coda_client: AsyncConductorQuantum):
        result = await async_coda_client.coda.health()
        assert result.get("status") == "ok"


class TestAsyncCodaTranspile:
    async def test_transpile(self, async_coda_client: AsyncConductorQuantum):
        result = await async_coda_client.coda.transpile(source_code=BELL_STATE_CODE, target="cirq")
        assert result.get("success") is True


class TestAsyncCodaAgents:
    async def test_agents_build_mode(self, async_coda_client: AsyncConductorQuantum):
        events = []
        async with async_skip_if_service_unavailable():
            async for event in async_coda_client.coda.agents(
                messages=[{"role": "user", "content": "What is a qubit?"}],
                mode="build",
                fast=True,
            ):
                events.append(event)
        _assert_agents_sse_invariants(events)
        assert len(events) >= 2
        assert events[-1]["type"] == "completed"

    async def test_agents_learn_mode(self, async_coda_client: AsyncConductorQuantum):
        events = []
        async with async_skip_if_service_unavailable():
            async for event in async_coda_client.coda.agents(
                messages=[{"role": "user", "content": "Define quantum superposition in one line."}],
                mode="learn",
                fast=True,
            ):
                events.append(event)
        _assert_agents_sse_invariants(events)
        assert events[-1]["type"] == "completed"


# ---------------------------------------------------------------------------
# Async new namespaced API (coda.tools.*, coda.agents.*)
# ---------------------------------------------------------------------------


class TestAsyncCodaToolsTranspile:
    async def test_transpile(self, async_coda_client: AsyncConductorQuantum):
        result = await async_coda_client.coda.tools.transpile(source_code=BELL_STATE_CODE, target="cirq")
        assert result.get("success") is True
        assert result.get("target_framework") == "cirq"
        converted = result.get("converted_code", "")
        assert isinstance(converted, str) and len(converted) > 0


class TestAsyncCodaAgentsRun:
    async def test_agents_run_build(self, async_coda_client: AsyncConductorQuantum):
        events = []
        async with async_skip_if_service_unavailable():
            async for event in async_coda_client.coda.agents.run(
                messages=[{"role": "user", "content": "What is a qubit?"}],
                mode="build",
                fast=True,
            ):
                events.append(event)
        _assert_agents_sse_invariants(events)
        assert len(events) >= 2
        assert events[-1]["type"] == "completed"


class TestAsyncCodaAgentsList:
    async def test_agents_list(self, async_coda_client: AsyncConductorQuantum):
        async with async_skip_if_service_unavailable():
            result = await async_coda_client.coda.agents.list()
        assert isinstance(result, dict)
        assert "agents" in result or "modes" in result
