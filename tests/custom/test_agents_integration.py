"""Integration tests for the Control API agents endpoints.

These tests run against the live API at https://api.conductorquantum.com/v0/control
and require a valid API key set via the CONTROL_API_TOKEN or CONDUCTOR_QUANTUM_API_KEY
environment variable.

Usage:
    CONTROL_API_TOKEN=<key> pytest tests/custom/test_agents_integration.py -v
"""

from __future__ import annotations

import os

import pytest
from conductorquantum import (
    AgentPublic,
    AsyncConductorQuantum,
    ConductorQuantum,
)
from conductorquantum.core.api_error import ApiError

_skip_no_key = pytest.mark.skipif(
    not (os.environ.get("CONTROL_API_TOKEN") or os.environ.get("CONDUCTOR_QUANTUM_API_KEY")),
    reason="Set CONTROL_API_TOKEN or CONDUCTOR_QUANTUM_API_KEY",
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
# Async Client
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
# Agents Run
# ---------------------------------------------------------------------------


class TestAgentsRun:
    def test_run_returns_dict(self, client: ConductorQuantum) -> None:
        agents = client.control.agents.list()
        if not agents:
            pytest.skip("No agents available for this token")
        agent = agents[0]
        try:
            result = client.control.agents.run(agent.id, body={"message": "test"})
        except ApiError as exc:
            if exc.status_code in (400, 422):
                pytest.skip(f"Agent {agent.id} requires specific body schema: {exc}")
            raise
        assert isinstance(result, dict)


class TestAsyncAgentsRun:
    async def test_run_returns_dict(self, async_client: AsyncConductorQuantum) -> None:
        agents = await async_client.control.agents.list()
        if not agents:
            pytest.skip("No agents available for this token")
        agent = agents[0]
        try:
            result = await async_client.control.agents.run(agent.id, body={"message": "test"})
        except ApiError as exc:
            if exc.status_code in (400, 422):
                pytest.skip(f"Agent {agent.id} requires specific body schema: {exc}")
            raise
        assert isinstance(result, dict)
