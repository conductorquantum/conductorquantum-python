from __future__ import annotations

import typing

import httpx
from .base_client import AsyncBaseConductorQuantum, BaseConductorQuantum
from .environment import ConductorQuantumEnvironment
from .models.extended_client import AsyncExtendedModelsClient, ExtendedModelsClient
from .coda.client import AsyncCodaClient, CodaClient
from .version import __version__

DEFAULT_TIMEOUT_SECONDS = 120

class ConductorQuantum(BaseConductorQuantum):
    """Main client for interacting with the Conductor Quantum API."""

    def __init__(
        self,
        *,
        base_url: typing.Optional[str] = None,
        environment: ConductorQuantumEnvironment = ConductorQuantumEnvironment.DEFAULT,
        token: typing.Union[str, typing.Callable[[], str]],
        timeout: typing.Optional[float] = DEFAULT_TIMEOUT_SECONDS,
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
        self._models = ExtendedModelsClient(client_wrapper=self._client_wrapper)

        resolved_token = token if isinstance(token, str) else token()
        resolved_base_url = base_url or environment.value
        self._coda = CodaClient(
            token=resolved_token,
            base_url=resolved_base_url,
            timeout=timeout or DEFAULT_TIMEOUT_SECONDS,
            sdk_version=__version__,
        )

    @property
    def coda(self) -> CodaClient:
        """Coda quantum computing API — circuit tools, QPU, and agents."""
        return self._coda


class AsyncConductorQuantum(AsyncBaseConductorQuantum):
    """Asynchronous client for interacting with the Conductor Quantum API."""

    def __init__(
        self,
        *,
        base_url: typing.Optional[str] = None,
        environment: ConductorQuantumEnvironment = ConductorQuantumEnvironment.DEFAULT,
        token: typing.Union[str, typing.Callable[[], str]],
        timeout: typing.Optional[float] = DEFAULT_TIMEOUT_SECONDS,
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
        self._models = AsyncExtendedModelsClient(client_wrapper=self._client_wrapper)

        resolved_token = token if isinstance(token, str) else token()
        resolved_base_url = base_url or environment.value
        self._coda = AsyncCodaClient(
            token=resolved_token,
            base_url=resolved_base_url,
            timeout=timeout or DEFAULT_TIMEOUT_SECONDS,
            sdk_version=__version__,
        )

    @property
    def coda(self) -> AsyncCodaClient:
        """Coda quantum computing API — circuit tools, QPU, and agents."""
        return self._coda
