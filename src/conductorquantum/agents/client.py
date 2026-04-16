"""Agents client for the Control API.

``client.control.agents.list()``  — list available agents
``client.control.agents.run(...)`` — execute an agent by ID
"""

from __future__ import annotations

import typing
from json.decoder import JSONDecodeError

from ..core.api_error import ApiError
from ..core.client_wrapper import AsyncClientWrapper, SyncClientWrapper
from ..core.jsonable_encoder import jsonable_encoder
from ..core.pydantic_utilities import parse_obj_as
from ..core.request_options import RequestOptions
from ..types.agent_public import AgentPublic


class AgentsClient:
    """Sync client for Control API agents (``/agents``)."""

    def __init__(self, *, client_wrapper: SyncClientWrapper) -> None:
        self._client_wrapper = client_wrapper

    def list(
        self,
        *,
        skip: typing.Optional[int] = None,
        limit: typing.Optional[int] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.List[AgentPublic]:
        """List agents the authenticated user can access.

        Parameters
        ----------
        skip : int, optional
            Number of agents to skip.
        limit : int, optional
            Max number of agents to return.
        request_options : RequestOptions, optional
            Request-specific configuration.

        Returns
        -------
        list[AgentPublic]
        """
        params: typing.Dict[str, typing.Any] = {}
        if skip is not None:
            params["skip"] = skip
        if limit is not None:
            params["limit"] = limit

        _response = self._client_wrapper.httpx_client.request(
            "agents",
            method="GET",
            params=params,
            request_options=request_options,
        )
        try:
            if 200 <= _response.status_code < 300:
                return typing.cast(
                    typing.List[AgentPublic],
                    parse_obj_as(
                        type_=typing.List[AgentPublic],  # type: ignore
                        object_=_response.json(),
                    ),
                )
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(
                status_code=_response.status_code,
                headers=dict(_response.headers),
                body=_response.text,
            )
        raise ApiError(
            status_code=_response.status_code,
            headers=dict(_response.headers),
            body=_response_json,
        )

    def run(
        self,
        agent_id: str,
        *,
        body: typing.Dict[str, typing.Any],
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.Dict[str, typing.Any]:
        """Execute an agent by its string ID.

        Parameters
        ----------
        agent_id : str
            The string ID of the agent (e.g. ``"ising-calibration-v1"``).
        body : dict
            Agent-specific request body.
        request_options : RequestOptions, optional
            Request-specific configuration.

        Returns
        -------
        dict
            Agent-specific response.
        """
        _response = self._client_wrapper.httpx_client.request(
            f"agents/{jsonable_encoder(agent_id)}",
            method="POST",
            json=body,
            request_options=request_options,
        )
        try:
            if 200 <= _response.status_code < 300:
                return typing.cast(typing.Dict[str, typing.Any], _response.json())
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(
                status_code=_response.status_code,
                headers=dict(_response.headers),
                body=_response.text,
            )
        raise ApiError(
            status_code=_response.status_code,
            headers=dict(_response.headers),
            body=_response_json,
        )


class AsyncAgentsClient:
    """Async client for Control API agents (``/agents``)."""

    def __init__(self, *, client_wrapper: AsyncClientWrapper) -> None:
        self._client_wrapper = client_wrapper

    async def list(
        self,
        *,
        skip: typing.Optional[int] = None,
        limit: typing.Optional[int] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.List[AgentPublic]:
        """List agents the authenticated user can access."""
        params: typing.Dict[str, typing.Any] = {}
        if skip is not None:
            params["skip"] = skip
        if limit is not None:
            params["limit"] = limit

        _response = await self._client_wrapper.httpx_client.request(
            "agents",
            method="GET",
            params=params,
            request_options=request_options,
        )
        try:
            if 200 <= _response.status_code < 300:
                return typing.cast(
                    typing.List[AgentPublic],
                    parse_obj_as(
                        type_=typing.List[AgentPublic],  # type: ignore
                        object_=_response.json(),
                    ),
                )
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(
                status_code=_response.status_code,
                headers=dict(_response.headers),
                body=_response.text,
            )
        raise ApiError(
            status_code=_response.status_code,
            headers=dict(_response.headers),
            body=_response_json,
        )

    async def run(
        self,
        agent_id: str,
        *,
        body: typing.Dict[str, typing.Any],
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.Dict[str, typing.Any]:
        """Execute an agent by its string ID."""
        _response = await self._client_wrapper.httpx_client.request(
            f"agents/{jsonable_encoder(agent_id)}",
            method="POST",
            json=body,
            request_options=request_options,
        )
        try:
            if 200 <= _response.status_code < 300:
                return typing.cast(typing.Dict[str, typing.Any], _response.json())
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(
                status_code=_response.status_code,
                headers=dict(_response.headers),
                body=_response.text,
            )
        raise ApiError(
            status_code=_response.status_code,
            headers=dict(_response.headers),
            body=_response_json,
        )
