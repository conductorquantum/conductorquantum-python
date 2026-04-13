"""Synchronous and asynchronous Coda API clients.

These clients provide access to quantum circuit tools, QPU submission,
and AI agent chat via the Coda ``/v0`` HTTP API.
"""

from __future__ import annotations

import json
from collections.abc import AsyncIterator, Iterator
from typing import Any

import httpx

from conductorquantum.coda._http import (
    DEFAULT_BASE_URL,
    DEFAULT_TIMEOUT,
    TokenAuth,
    TokenLike,
    async_request,
    build_headers,
    parse_json,
    sync_request,
)


class CodaClient:
    """Synchronous client for the Coda quantum computing API.

    Typically accessed via ``ConductorQuantum(...).coda`` rather than
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
        self._client = httpx.Client(
            base_url=base_url,
            headers=build_headers(sdk_version),
            auth=TokenAuth(token),
            timeout=timeout,
        )

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._client.close()

    # === Health ===

    def health(self) -> dict[str, Any]:
        """Check API health."""
        resp = sync_request(self._client, "GET", "/health")
        return parse_json(resp)

    # === Quantum Circuit Tools ===

    def transpile(self, *, source_code: str, target: str) -> dict[str, Any]:
        """Transpile quantum code to a target framework."""
        resp = sync_request(self._client, "POST", "/transpile", json={"source_code": source_code, "target": target})
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
        resp = sync_request(self._client, "POST", "/simulate", json=body)
        return parse_json(resp)

    def to_openqasm3(self, *, code: str) -> dict[str, Any]:
        """Convert a quantum circuit to OpenQASM 3.0."""
        resp = sync_request(self._client, "POST", "/to-openqasm3", json={"code": code})
        return parse_json(resp)

    def estimate_resources(self, *, code: str) -> dict[str, Any]:
        """Estimate resource requirements for a quantum circuit."""
        resp = sync_request(self._client, "POST", "/estimate-resources", json={"code": code})
        return parse_json(resp)

    def split_circuit(self, *, code: str) -> dict[str, Any]:
        """Split a circuit using circuit cutting."""
        resp = sync_request(self._client, "POST", "/split-circuit", json={"code": code})
        return parse_json(resp)

    # === QPU ===

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
        resp = sync_request(self._client, "POST", "/qpu/submit", json=body)
        return parse_json(resp)

    def qpu_status(self, *, job_id: str) -> dict[str, Any]:
        """Check status of a submitted QPU job."""
        resp = sync_request(self._client, "POST", "/qpu/status", json={"job_id": job_id})
        return parse_json(resp)

    def qpu_devices(self) -> dict[str, Any]:
        """List available QPU devices."""
        resp = sync_request(self._client, "GET", "/qpu/devices")
        return parse_json(resp)

    def qpu_estimate_cost(
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
        resp = sync_request(self._client, "POST", "/qpu/estimate-cost", json=body)
        return parse_json(resp)

    # === Agents ===

    def agents(
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
            auth=TokenAuth(token),
            timeout=timeout,
        )

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        await self._client.aclose()

    # === Health ===

    async def health(self) -> dict[str, Any]:
        """Check API health."""
        resp = await async_request(self._client, "GET", "/health")
        return parse_json(resp)

    # === Quantum Circuit Tools ===

    async def transpile(self, *, source_code: str, target: str) -> dict[str, Any]:
        """Transpile quantum code to a target framework."""
        resp = await async_request(
            self._client, "POST", "/transpile", json={"source_code": source_code, "target": target}
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
        resp = await async_request(self._client, "POST", "/simulate", json=body)
        return parse_json(resp)

    async def to_openqasm3(self, *, code: str) -> dict[str, Any]:
        """Convert a quantum circuit to OpenQASM 3.0."""
        resp = await async_request(self._client, "POST", "/to-openqasm3", json={"code": code})
        return parse_json(resp)

    async def estimate_resources(self, *, code: str) -> dict[str, Any]:
        """Estimate resource requirements for a quantum circuit."""
        resp = await async_request(self._client, "POST", "/estimate-resources", json={"code": code})
        return parse_json(resp)

    async def split_circuit(self, *, code: str) -> dict[str, Any]:
        """Split a circuit using circuit cutting."""
        resp = await async_request(self._client, "POST", "/split-circuit", json={"code": code})
        return parse_json(resp)

    # === QPU ===

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
        resp = await async_request(self._client, "POST", "/qpu/submit", json=body)
        return parse_json(resp)

    async def qpu_status(self, *, job_id: str) -> dict[str, Any]:
        """Check status of a submitted QPU job."""
        resp = await async_request(self._client, "POST", "/qpu/status", json={"job_id": job_id})
        return parse_json(resp)

    async def qpu_devices(self) -> dict[str, Any]:
        """List available QPU devices."""
        resp = await async_request(self._client, "GET", "/qpu/devices")
        return parse_json(resp)

    async def qpu_estimate_cost(
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
        resp = await async_request(self._client, "POST", "/qpu/estimate-cost", json=body)
        return parse_json(resp)

    # === Agents ===

    async def agents(
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
