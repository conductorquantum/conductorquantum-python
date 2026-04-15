"""Synchronous and asynchronous Coda API clients.

These clients provide access to quantum circuit tools, QPU submission,
and AI agent chat via the Coda ``/v0/coda`` HTTP API.
"""

from __future__ import annotations

import json
import warnings
from collections.abc import AsyncIterator, Iterator
from typing import Any

import httpx

from conductorquantum.coda._http import (
    DEFAULT_BASE_URL,
    DEFAULT_TIMEOUT,
    CodaTokenAuth,
    TokenLike,
    async_request,
    build_headers,
    parse_json,
    sync_request,
)

# ── Sync sub-clients ─────────────────────────────────────────────────────────


class CodaToolsClient:
    """Quantum circuit tools: transpile, simulate, convert, estimate, and split."""

    def __init__(self, client: httpx.Client) -> None:
        self._client = client

    def list(self) -> dict[str, Any]:
        """List available quantum circuit tools."""
        resp = sync_request(self._client, "GET", "/tools")
        return parse_json(resp)

    def transpile(self, *, source_code: str, target: str) -> dict[str, Any]:
        """Transpile quantum code to a target framework."""
        resp = sync_request(self._client, "POST", "/tools/transpile", json={"source_code": source_code, "target": target})
        return parse_json(resp)

    def simulate(
        self,
        *,
        code: str,
        method: str = "qasm",
        shots: int = 1024,
        seed_simulator: int | None = None,
        backend: str = "auto",
    ) -> dict[str, Any]:
        """Simulate a quantum circuit."""
        body: dict[str, Any] = {"code": code, "method": method, "shots": shots, "backend": backend}
        if seed_simulator is not None:
            body["seed_simulator"] = seed_simulator
        resp = sync_request(self._client, "POST", "/tools/simulate", json=body)
        return parse_json(resp)

    def to_openqasm3(self, *, code: str) -> dict[str, Any]:
        """Convert a quantum circuit to OpenQASM 3.0."""
        resp = sync_request(self._client, "POST", "/tools/to-openqasm3", json={"code": code})
        return parse_json(resp)

    def estimate_resources(self, *, code: str) -> dict[str, Any]:
        """Estimate resource requirements for a quantum circuit."""
        resp = sync_request(self._client, "POST", "/tools/estimate-resources", json={"code": code})
        return parse_json(resp)

    def split_circuit(self, *, code: str) -> dict[str, Any]:
        """Split a circuit using circuit cutting."""
        resp = sync_request(self._client, "POST", "/tools/split-circuit", json={"code": code})
        return parse_json(resp)


class CodaQPUsClient:
    """QPU operations: submit jobs, check status, list devices, estimate cost."""

    def __init__(self, client: httpx.Client) -> None:
        self._client = client

    def run(
        self,
        *,
        code: str,
        source_framework: str,
        backend: str,
        shots: int = 100,
        accept_overage: bool = False,
        braket_execution_mode_hint: str | None = None,
    ) -> dict[str, Any]:
        """Submit a circuit to a QPU backend."""
        body: dict[str, Any] = {
            "code": code,
            "source_framework": source_framework,
            "backend": backend,
            "shots": shots,
            "accept_overage": accept_overage,
        }
        if braket_execution_mode_hint is not None:
            body["braket_execution_mode_hint"] = braket_execution_mode_hint
        resp = sync_request(self._client, "POST", "/qpus", json=body)
        return parse_json(resp)

    def status(self, *, job_id: str) -> dict[str, Any]:
        """Check status of a submitted QPU job."""
        resp = sync_request(self._client, "POST", "/qpus/status", json={"job_id": job_id})
        return parse_json(resp)

    def list(self) -> dict[str, Any]:
        """List available QPU devices."""
        resp = sync_request(self._client, "GET", "/qpus")
        return parse_json(resp)

    def estimate_cost(
        self,
        *,
        code: str,
        source_framework: str,
        backend: str,
        shots: int = 100,
        braket_execution_mode_hint: str | None = None,
    ) -> dict[str, Any]:
        """Estimate cost for a QPU job without submitting."""
        body: dict[str, Any] = {
            "code": code,
            "source_framework": source_framework,
            "backend": backend,
            "shots": shots,
        }
        if braket_execution_mode_hint is not None:
            body["braket_execution_mode_hint"] = braket_execution_mode_hint
        resp = sync_request(self._client, "POST", "/qpus/estimate-cost", json=body)
        return parse_json(resp)


class CodaAgentsClient:
    """Agent operations: chat (SSE) and list available modes."""

    def __init__(self, client: httpx.Client) -> None:
        self._client = client

    def run(
        self,
        *,
        messages: list[dict[str, str]],
        thread_id: str | None = None,
        fast: bool = False,
        mode: str = "build",
    ) -> Iterator[dict[str, Any]]:
        """Chat with a Coda agent. Returns an iterator of SSE events.

        Each event is a dict with at least a ``type`` field. Terminal events
        have ``type`` of ``completed``, ``error``, or ``cancelled``.
        """
        body: dict[str, Any] = {"messages": messages, "fast": fast, "mode": mode}
        if thread_id is not None:
            body["thread_id"] = thread_id

        with self._client.stream("POST", "/agents", json=body) as response:
            if not response.is_success:
                response.read()
                parse_json(response)

            for line in response.iter_lines():
                if line.startswith("data: "):
                    try:
                        yield json.loads(line[6:])
                    except json.JSONDecodeError:
                        continue

    def list(self) -> dict[str, Any]:
        """List available agent modes."""
        resp = sync_request(self._client, "GET", "/agents")
        return parse_json(resp)

    def __call__(self, **kwargs: Any) -> Iterator[dict[str, Any]]:
        # TODO(v2): Remove __call__ bridge; callers should use .run()
        warnings.warn(
            "client.coda.agents(...) is deprecated; use client.coda.agents.run(...) instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.run(**kwargs)


# ── Async sub-clients ─────────────────────────────────────────────────────────


class AsyncCodaToolsClient:
    """Async quantum circuit tools: transpile, simulate, convert, estimate, and split."""

    def __init__(self, client: httpx.AsyncClient) -> None:
        self._client = client

    async def list(self) -> dict[str, Any]:
        """List available quantum circuit tools."""
        resp = await async_request(self._client, "GET", "/tools")
        return parse_json(resp)

    async def transpile(self, *, source_code: str, target: str) -> dict[str, Any]:
        """Transpile quantum code to a target framework."""
        resp = await async_request(
            self._client, "POST", "/tools/transpile", json={"source_code": source_code, "target": target}
        )
        return parse_json(resp)

    async def simulate(
        self,
        *,
        code: str,
        method: str = "qasm",
        shots: int = 1024,
        seed_simulator: int | None = None,
        backend: str = "auto",
    ) -> dict[str, Any]:
        """Simulate a quantum circuit."""
        body: dict[str, Any] = {"code": code, "method": method, "shots": shots, "backend": backend}
        if seed_simulator is not None:
            body["seed_simulator"] = seed_simulator
        resp = await async_request(self._client, "POST", "/tools/simulate", json=body)
        return parse_json(resp)

    async def to_openqasm3(self, *, code: str) -> dict[str, Any]:
        """Convert a quantum circuit to OpenQASM 3.0."""
        resp = await async_request(self._client, "POST", "/tools/to-openqasm3", json={"code": code})
        return parse_json(resp)

    async def estimate_resources(self, *, code: str) -> dict[str, Any]:
        """Estimate resource requirements for a quantum circuit."""
        resp = await async_request(self._client, "POST", "/tools/estimate-resources", json={"code": code})
        return parse_json(resp)

    async def split_circuit(self, *, code: str) -> dict[str, Any]:
        """Split a circuit using circuit cutting."""
        resp = await async_request(self._client, "POST", "/tools/split-circuit", json={"code": code})
        return parse_json(resp)


class AsyncCodaQPUsClient:
    """Async QPU operations: submit jobs, check status, list devices, estimate cost."""

    def __init__(self, client: httpx.AsyncClient) -> None:
        self._client = client

    async def run(
        self,
        *,
        code: str,
        source_framework: str,
        backend: str,
        shots: int = 100,
        accept_overage: bool = False,
        braket_execution_mode_hint: str | None = None,
    ) -> dict[str, Any]:
        """Submit a circuit to a QPU backend."""
        body: dict[str, Any] = {
            "code": code,
            "source_framework": source_framework,
            "backend": backend,
            "shots": shots,
            "accept_overage": accept_overage,
        }
        if braket_execution_mode_hint is not None:
            body["braket_execution_mode_hint"] = braket_execution_mode_hint
        resp = await async_request(self._client, "POST", "/qpus", json=body)
        return parse_json(resp)

    async def status(self, *, job_id: str) -> dict[str, Any]:
        """Check status of a submitted QPU job."""
        resp = await async_request(self._client, "POST", "/qpus/status", json={"job_id": job_id})
        return parse_json(resp)

    async def list(self) -> dict[str, Any]:
        """List available QPU devices."""
        resp = await async_request(self._client, "GET", "/qpus")
        return parse_json(resp)

    async def estimate_cost(
        self,
        *,
        code: str,
        source_framework: str,
        backend: str,
        shots: int = 100,
        braket_execution_mode_hint: str | None = None,
    ) -> dict[str, Any]:
        """Estimate cost for a QPU job without submitting."""
        body: dict[str, Any] = {
            "code": code,
            "source_framework": source_framework,
            "backend": backend,
            "shots": shots,
        }
        if braket_execution_mode_hint is not None:
            body["braket_execution_mode_hint"] = braket_execution_mode_hint
        resp = await async_request(self._client, "POST", "/qpus/estimate-cost", json=body)
        return parse_json(resp)


class AsyncCodaAgentsClient:
    """Async agent operations: chat (SSE) and list available modes."""

    def __init__(self, client: httpx.AsyncClient) -> None:
        self._client = client

    async def run(
        self,
        *,
        messages: list[dict[str, str]],
        thread_id: str | None = None,
        fast: bool = False,
        mode: str = "build",
    ) -> AsyncIterator[dict[str, Any]]:
        """Chat with a Coda agent. Returns an async iterator of SSE events.

        Each event is a dict with at least a ``type`` field. Terminal events
        have ``type`` of ``completed``, ``error``, or ``cancelled``.
        """
        body: dict[str, Any] = {"messages": messages, "fast": fast, "mode": mode}
        if thread_id is not None:
            body["thread_id"] = thread_id

        async with self._client.stream("POST", "/agents", json=body) as response:
            if not response.is_success:
                await response.aread()
                parse_json(response)

            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    try:
                        yield json.loads(line[6:])
                    except json.JSONDecodeError:
                        continue

    async def list(self) -> dict[str, Any]:
        """List available agent modes."""
        resp = await async_request(self._client, "GET", "/agents")
        return parse_json(resp)

    def __call__(self, **kwargs: Any) -> AsyncIterator[dict[str, Any]]:
        # TODO(v2): Remove __call__ bridge; callers should use .run()
        warnings.warn(
            "client.coda.agents(...) is deprecated; use client.coda.agents.run(...) instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.run(**kwargs)


# ── Main clients ──────────────────────────────────────────────────────────────


class CodaClient:
    """Synchronous client for the Coda quantum computing API.

    Typically accessed via ``ConductorQuantum(...).coda`` rather than
    instantiated directly.

    Namespaced access::

        client.coda.tools.transpile(...)
        client.coda.qpus.run(...)
        client.coda.agents.run(...)
    """

    def __init__(
        self,
        *,
        token: TokenLike,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        sdk_version: str = "0.0.0",
    ) -> None:
        self._client = httpx.Client(
            base_url=base_url,
            headers=build_headers(sdk_version),
            auth=CodaTokenAuth(token),
            timeout=timeout,
        )
        self._tools = CodaToolsClient(self._client)
        self._qpus = CodaQPUsClient(self._client)
        self._agents = CodaAgentsClient(self._client)

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._client.close()

    @property
    def tools(self) -> CodaToolsClient:
        """Quantum circuit tools sub-client."""
        return self._tools

    @property
    def qpus(self) -> CodaQPUsClient:
        """QPU operations sub-client."""
        return self._qpus

    @property
    def agents(self) -> CodaAgentsClient:
        """Agents sub-client."""
        return self._agents

    # === Health ===

    def health(self) -> dict[str, Any]:
        """Check API health."""
        resp = sync_request(self._client, "GET", "/health")
        return parse_json(resp)

    # === Deprecated methods (delegate to sub-clients) ===

    def transpile(self, *, source_code: str, target: str) -> dict[str, Any]:
        # TODO(v2): Remove deprecated CodaClient.transpile(); use .tools.transpile()
        warnings.warn(
            "client.coda.transpile() is deprecated; use client.coda.tools.transpile() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self._tools.transpile(source_code=source_code, target=target)

    def simulate(
        self,
        *,
        code: str,
        method: str = "qasm",
        shots: int = 1024,
        seed_simulator: int | None = None,
        backend: str = "auto",
    ) -> dict[str, Any]:
        # TODO(v2): Remove deprecated CodaClient.simulate(); use .tools.simulate()
        warnings.warn(
            "client.coda.simulate() is deprecated; use client.coda.tools.simulate() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self._tools.simulate(
            code=code, method=method, shots=shots, seed_simulator=seed_simulator, backend=backend
        )

    def to_openqasm3(self, *, code: str) -> dict[str, Any]:
        # TODO(v2): Remove deprecated CodaClient.to_openqasm3(); use .tools.to_openqasm3()
        warnings.warn(
            "client.coda.to_openqasm3() is deprecated; use client.coda.tools.to_openqasm3() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self._tools.to_openqasm3(code=code)

    def estimate_resources(self, *, code: str) -> dict[str, Any]:
        # TODO(v2): Remove deprecated CodaClient.estimate_resources(); use .tools.estimate_resources()
        warnings.warn(
            "client.coda.estimate_resources() is deprecated; use client.coda.tools.estimate_resources() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self._tools.estimate_resources(code=code)

    def split_circuit(self, *, code: str) -> dict[str, Any]:
        # TODO(v2): Remove deprecated CodaClient.split_circuit(); use .tools.split_circuit()
        warnings.warn(
            "client.coda.split_circuit() is deprecated; use client.coda.tools.split_circuit() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self._tools.split_circuit(code=code)

    def qpu_submit(
        self,
        *,
        code: str,
        source_framework: str,
        backend: str,
        shots: int = 100,
        accept_overage: bool = False,
        braket_execution_mode_hint: str | None = None,
    ) -> dict[str, Any]:
        # TODO(v2): Remove deprecated CodaClient.qpu_submit(); use .qpus.run()
        warnings.warn(
            "client.coda.qpu_submit() is deprecated; use client.coda.qpus.run() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self._qpus.run(
            code=code,
            source_framework=source_framework,
            backend=backend,
            shots=shots,
            accept_overage=accept_overage,
            braket_execution_mode_hint=braket_execution_mode_hint,
        )

    def qpu_status(self, *, job_id: str) -> dict[str, Any]:
        # TODO(v2): Remove deprecated CodaClient.qpu_status(); use .qpus.status()
        warnings.warn(
            "client.coda.qpu_status() is deprecated; use client.coda.qpus.status() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self._qpus.status(job_id=job_id)

    def qpu_devices(self) -> dict[str, Any]:
        # TODO(v2): Remove deprecated CodaClient.qpu_devices(); use .qpus.list()
        warnings.warn(
            "client.coda.qpu_devices() is deprecated; use client.coda.qpus.list() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self._qpus.list()

    def qpu_estimate_cost(
        self,
        *,
        code: str,
        source_framework: str,
        backend: str,
        shots: int = 100,
        braket_execution_mode_hint: str | None = None,
    ) -> dict[str, Any]:
        # TODO(v2): Remove deprecated CodaClient.qpu_estimate_cost(); use .qpus.estimate_cost()
        warnings.warn(
            "client.coda.qpu_estimate_cost() is deprecated; use client.coda.qpus.estimate_cost() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self._qpus.estimate_cost(
            code=code,
            source_framework=source_framework,
            backend=backend,
            shots=shots,
            braket_execution_mode_hint=braket_execution_mode_hint,
        )

    def agents_list(self) -> dict[str, Any]:
        # TODO(v2): Remove deprecated CodaClient.agents_list(); use .agents.list()
        warnings.warn(
            "client.coda.agents_list() is deprecated; use client.coda.agents.list() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self._agents.list()


class AsyncCodaClient:
    """Asynchronous client for the Coda quantum computing API.

    Typically accessed via ``AsyncConductorQuantum(...).coda`` rather than
    instantiated directly.
    """

    def __init__(
        self,
        *,
        token: TokenLike,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        sdk_version: str = "0.0.0",
    ) -> None:
        self._client = httpx.AsyncClient(
            base_url=base_url,
            headers=build_headers(sdk_version),
            auth=CodaTokenAuth(token),
            timeout=timeout,
        )
        self._tools = AsyncCodaToolsClient(self._client)
        self._qpus = AsyncCodaQPUsClient(self._client)
        self._agents = AsyncCodaAgentsClient(self._client)

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        await self._client.aclose()

    @property
    def tools(self) -> AsyncCodaToolsClient:
        """Quantum circuit tools sub-client."""
        return self._tools

    @property
    def qpus(self) -> AsyncCodaQPUsClient:
        """QPU operations sub-client."""
        return self._qpus

    @property
    def agents(self) -> AsyncCodaAgentsClient:
        """Agents sub-client."""
        return self._agents

    # === Health ===

    async def health(self) -> dict[str, Any]:
        """Check API health."""
        resp = await async_request(self._client, "GET", "/health")
        return parse_json(resp)

    # === Deprecated methods (delegate to sub-clients) ===

    async def transpile(self, *, source_code: str, target: str) -> dict[str, Any]:
        # TODO(v2): Remove deprecated AsyncCodaClient.transpile(); use .tools.transpile()
        warnings.warn(
            "client.coda.transpile() is deprecated; use client.coda.tools.transpile() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return await self._tools.transpile(source_code=source_code, target=target)

    async def simulate(
        self,
        *,
        code: str,
        method: str = "qasm",
        shots: int = 1024,
        seed_simulator: int | None = None,
        backend: str = "auto",
    ) -> dict[str, Any]:
        # TODO(v2): Remove deprecated AsyncCodaClient.simulate(); use .tools.simulate()
        warnings.warn(
            "client.coda.simulate() is deprecated; use client.coda.tools.simulate() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return await self._tools.simulate(
            code=code, method=method, shots=shots, seed_simulator=seed_simulator, backend=backend
        )

    async def to_openqasm3(self, *, code: str) -> dict[str, Any]:
        # TODO(v2): Remove deprecated AsyncCodaClient.to_openqasm3(); use .tools.to_openqasm3()
        warnings.warn(
            "client.coda.to_openqasm3() is deprecated; use client.coda.tools.to_openqasm3() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return await self._tools.to_openqasm3(code=code)

    async def estimate_resources(self, *, code: str) -> dict[str, Any]:
        # TODO(v2): Remove deprecated AsyncCodaClient.estimate_resources(); use .tools.estimate_resources()
        warnings.warn(
            "client.coda.estimate_resources() is deprecated; use client.coda.tools.estimate_resources() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return await self._tools.estimate_resources(code=code)

    async def split_circuit(self, *, code: str) -> dict[str, Any]:
        # TODO(v2): Remove deprecated AsyncCodaClient.split_circuit(); use .tools.split_circuit()
        warnings.warn(
            "client.coda.split_circuit() is deprecated; use client.coda.tools.split_circuit() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return await self._tools.split_circuit(code=code)

    async def qpu_submit(
        self,
        *,
        code: str,
        source_framework: str,
        backend: str,
        shots: int = 100,
        accept_overage: bool = False,
        braket_execution_mode_hint: str | None = None,
    ) -> dict[str, Any]:
        # TODO(v2): Remove deprecated AsyncCodaClient.qpu_submit(); use .qpus.run()
        warnings.warn(
            "client.coda.qpu_submit() is deprecated; use client.coda.qpus.run() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return await self._qpus.run(
            code=code,
            source_framework=source_framework,
            backend=backend,
            shots=shots,
            accept_overage=accept_overage,
            braket_execution_mode_hint=braket_execution_mode_hint,
        )

    async def qpu_status(self, *, job_id: str) -> dict[str, Any]:
        # TODO(v2): Remove deprecated AsyncCodaClient.qpu_status(); use .qpus.status()
        warnings.warn(
            "client.coda.qpu_status() is deprecated; use client.coda.qpus.status() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return await self._qpus.status(job_id=job_id)

    async def qpu_devices(self) -> dict[str, Any]:
        # TODO(v2): Remove deprecated AsyncCodaClient.qpu_devices(); use .qpus.list()
        warnings.warn(
            "client.coda.qpu_devices() is deprecated; use client.coda.qpus.list() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return await self._qpus.list()

    async def qpu_estimate_cost(
        self,
        *,
        code: str,
        source_framework: str,
        backend: str,
        shots: int = 100,
        braket_execution_mode_hint: str | None = None,
    ) -> dict[str, Any]:
        # TODO(v2): Remove deprecated AsyncCodaClient.qpu_estimate_cost(); use .qpus.estimate_cost()
        warnings.warn(
            "client.coda.qpu_estimate_cost() is deprecated; use client.coda.qpus.estimate_cost() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return await self._qpus.estimate_cost(
            code=code,
            source_framework=source_framework,
            backend=backend,
            shots=shots,
            braket_execution_mode_hint=braket_execution_mode_hint,
        )

    async def agents_list(self) -> dict[str, Any]:
        # TODO(v2): Remove deprecated AsyncCodaClient.agents_list(); use .agents.list()
        warnings.warn(
            "client.coda.agents_list() is deprecated; use client.coda.agents.list() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return await self._agents.list()
