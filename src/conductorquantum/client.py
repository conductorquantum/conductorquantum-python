from __future__ import annotations

import typing

import httpx

from .base_client import BaseConductorQuantum, AsyncBaseConductorQuantum
from .environment import ConductorQuantumEnvironment
from .models.extended_client import ExtendedModelsClient, AsyncExtendedModelsClient

class ConductorQuantum(BaseConductorQuantum):
    """Main client for interacting with the Conductor Quantum API."""

    def __init__(
        self,
        *,
        base_url: typing.Optional[str] = None,
        environment: ConductorQuantumEnvironment = ConductorQuantumEnvironment.DEFAULT,
        token: typing.Union[str, typing.Callable[[], str]],
        timeout: typing.Optional[float] = None,
        follow_redirects: typing.Optional[bool] = True,
        httpx_client: typing.Optional[httpx.Client] = None,
    ):
        super().__init__(
            base_url=base_url,
            environment=environment,
            token=token,
            timeout=timeout,
            follow_redirects=follow_redirects,
            httpx_client=httpx_client,
        )
        self.models = ExtendedModelsClient(client_wrapper=self._client_wrapper)


class AsyncConductorQuantum(AsyncBaseConductorQuantum):
    """Asynchronous client for interacting with the Conductor Quantum API."""

    def __init__(
        self,
        *,
        base_url: typing.Optional[str] = None,
        environment: ConductorQuantumEnvironment = ConductorQuantumEnvironment.DEFAULT,
        token: typing.Union[str, typing.Callable[[], str]],
        timeout: typing.Optional[float] = None,
        follow_redirects: typing.Optional[bool] = True,
        httpx_client: typing.Optional[httpx.AsyncClient] = None,
    ):
        super().__init__(
            base_url=base_url,
            environment=environment,
            token=token,
            timeout=timeout,
            follow_redirects=follow_redirects,
            httpx_client=httpx_client,
        )
        self.models = AsyncExtendedModelsClient(client_wrapper=self._client_wrapper)
