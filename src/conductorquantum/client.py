from __future__ import annotations

import typing
import warnings
from collections.abc import AsyncIterator, Iterator

import httpx
from .base_client import AsyncBaseConductorQuantum, BaseConductorQuantum
from .coda._http import api_base_url_from_env
from .coda.client import AsyncCodaClient, CodaClient
from .control import AsyncControlClient, ControlClient
from .environment import ConductorQuantumEnvironment
from .model_results.client import AsyncModelResultsClient, ModelResultsClient
from .models.extended_client import AsyncExtendedModelsClient, ExtendedModelsClient
from .version import __version__

DEFAULT_TIMEOUT_SECONDS = 120


_TokenArg = typing.Union[str, typing.Callable[[], str]]


class ConductorQuantum(BaseConductorQuantum):
    """Main client for interacting with the Conductor Quantum API.

    Authenticate with a single token::

          client = ConductorQuantum(token="MY_TOKEN")

    Namespaced access mirrors the product structure::

        client.coda.simulate(...)               # Coda — circuit tools, QPU, agents
        client.control.models.execute(...)       # Control — analysis models

    Non-conflicting methods are also available at the top level::

        client.simulate(...)        # shortcut for client.coda.simulate(...)
        client.agents(...)          # shortcut for client.coda.agents(...)

    Coda methods require a Coda API token that starts with ``coda_``. If you
    call ``client.coda.*`` or a top-level Coda shortcut with any other token,
    the SDK raises ``ValueError`` before sending the request.

    **Backwards compatibility:**

    ``client.models`` and ``client.model_results`` are inherited from the
    Fern-generated ``BaseConductorQuantum`` and still work. They are the same
    objects as ``client.control.models`` and ``client.control.model_results``.
    New code should prefer ``client.control.*`` to match the product structure.
    These legacy accessors will be removed in a future major version.
    """

    def __init__(
        self,
        *,
        base_url: typing.Optional[str] = None,
        environment: ConductorQuantumEnvironment = ConductorQuantumEnvironment.DEFAULT,
        token: typing.Optional[_TokenArg] = None,
        timeout: typing.Optional[float] = DEFAULT_TIMEOUT_SECONDS,
        follow_redirects: typing.Optional[bool] = True,
        httpx_client: typing.Optional[httpx.Client] = None,
    ):
        if token is None:
            raise ValueError("Provide token")

        super().__init__(
            base_url=base_url,
            environment=environment,
            token=token,
            timeout=timeout,
            follow_redirects=follow_redirects,
            httpx_client=httpx_client,
        )
        self._models = ExtendedModelsClient(client_wrapper=self._client_wrapper)
        _base_model_results = super(ConductorQuantum, self).model_results
        self._control = ControlClient(models=self._models, model_results=_base_model_results)

        coda_base_url = base_url or api_base_url_from_env()
        self._coda = CodaClient(
            token=token,
            base_url=coda_base_url,
            timeout=timeout or DEFAULT_TIMEOUT_SECONDS,
            sdk_version=__version__,
        )

    @property
    def control(self) -> ControlClient:
        """Control product line — analysis models and model results."""
        return self._control

    @property
    def coda(self) -> CodaClient:
        """Coda product line — circuit tools, QPU, and agents."""
        return self._coda

    # -- Backwards-compatible accessors (deprecated) --
    # These override the Fern-generated base class properties so we can
    # emit deprecation warnings. The base class defines them too, but
    # base_client.py is auto-generated and will be overwritten by Fern,
    # so the warnings must live here in the handwritten client.py.

    @property
    def models(self) -> ExtendedModelsClient:  # type: ignore[override]
        """**Deprecated.** Use ``client.control.models`` instead."""
        warnings.warn(
            "client.models is deprecated; use client.control.models instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self._control.models

    @property
    def model_results(self) -> ModelResultsClient:  # type: ignore[override]
        """**Deprecated.** Use ``client.control.model_results`` instead."""
        warnings.warn(
            "client.model_results is deprecated; use client.control.model_results instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self._control.model_results

    # -- Top-level Coda shortcuts (no name conflicts) --

    def health(self) -> dict[str, typing.Any]:
        """Shortcut for ``self.coda.health()``."""
        return self._coda.health()

    def transpile(self, *, source_code: str, target: str) -> dict[str, typing.Any]:
        """Shortcut for ``self.coda.transpile(...)``."""
        return self._coda.transpile(source_code=source_code, target=target)

    def simulate(
        self,
        *,
        code: str,
        method: str = "qasm",
        shots: int = 1024,
        seed_simulator: typing.Optional[int] = None,
        backend: str = "auto",
    ) -> dict[str, typing.Any]:
        """Shortcut for ``self.coda.simulate(...)``."""
        return self._coda.simulate(
            code=code, method=method, shots=shots, seed_simulator=seed_simulator, backend=backend
        )

    def to_openqasm3(self, *, code: str) -> dict[str, typing.Any]:
        """Shortcut for ``self.coda.to_openqasm3(...)``."""
        return self._coda.to_openqasm3(code=code)

    def estimate_resources(self, *, code: str) -> dict[str, typing.Any]:
        """Shortcut for ``self.coda.estimate_resources(...)``."""
        return self._coda.estimate_resources(code=code)

    def split_circuit(self, *, code: str) -> dict[str, typing.Any]:
        """Shortcut for ``self.coda.split_circuit(...)``."""
        return self._coda.split_circuit(code=code)

    def qpu_submit(
        self,
        *,
        code: str,
        source_framework: str,
        backend: str,
        shots: int = 100,
        accept_overage: bool = False,
        braket_execution_mode_hint: typing.Optional[str] = None,
    ) -> dict[str, typing.Any]:
        """Shortcut for ``self.coda.qpu_submit(...)``."""
        return self._coda.qpu_submit(
            code=code,
            source_framework=source_framework,
            backend=backend,
            shots=shots,
            accept_overage=accept_overage,
            braket_execution_mode_hint=braket_execution_mode_hint,
        )

    def qpu_status(self, *, job_id: str) -> dict[str, typing.Any]:
        """Shortcut for ``self.coda.qpu_status(...)``."""
        return self._coda.qpu_status(job_id=job_id)

    def qpu_devices(self) -> dict[str, typing.Any]:
        """Shortcut for ``self.coda.qpu_devices()``."""
        return self._coda.qpu_devices()

    def qpu_estimate_cost(
        self,
        *,
        code: str,
        source_framework: str,
        backend: str,
        shots: int = 100,
        braket_execution_mode_hint: typing.Optional[str] = None,
    ) -> dict[str, typing.Any]:
        """Shortcut for ``self.coda.qpu_estimate_cost(...)``."""
        return self._coda.qpu_estimate_cost(
            code=code,
            source_framework=source_framework,
            backend=backend,
            shots=shots,
            braket_execution_mode_hint=braket_execution_mode_hint,
        )

    def agents(
        self,
        *,
        messages: list[dict[str, str]],
        thread_id: typing.Optional[str] = None,
        fast: bool = False,
        mode: str = "build",
    ) -> Iterator[dict[str, typing.Any]]:
        """Shortcut for ``self.coda.agents(...)``."""
        return self._coda.agents(messages=messages, thread_id=thread_id, fast=fast, mode=mode)


class AsyncConductorQuantum(AsyncBaseConductorQuantum):
    """Asynchronous client for interacting with the Conductor Quantum API.

    See :class:`ConductorQuantum` for the full API description, including
    the single-token auth model, Coda token validation, and backwards
    compatibility notes.
    """

    def __init__(
        self,
        *,
        base_url: typing.Optional[str] = None,
        environment: ConductorQuantumEnvironment = ConductorQuantumEnvironment.DEFAULT,
        token: typing.Optional[_TokenArg] = None,
        timeout: typing.Optional[float] = DEFAULT_TIMEOUT_SECONDS,
        follow_redirects: typing.Optional[bool] = True,
        httpx_client: typing.Optional[httpx.AsyncClient] = None,
    ):
        if token is None:
            raise ValueError("Provide token")

        super().__init__(
            base_url=base_url,
            environment=environment,
            token=token,
            timeout=timeout,
            follow_redirects=follow_redirects,
            httpx_client=httpx_client,
        )
        self._models = AsyncExtendedModelsClient(client_wrapper=self._client_wrapper)
        _base_model_results = super(AsyncConductorQuantum, self).model_results
        self._control = AsyncControlClient(models=self._models, model_results=_base_model_results)

        coda_base_url = base_url or api_base_url_from_env()
        self._coda = AsyncCodaClient(
            token=token,
            base_url=coda_base_url,
            timeout=timeout or DEFAULT_TIMEOUT_SECONDS,
            sdk_version=__version__,
        )

    @property
    def control(self) -> AsyncControlClient:
        """Control product line — analysis models and model results."""
        return self._control

    @property
    def coda(self) -> AsyncCodaClient:
        """Coda product line — circuit tools, QPU, and agents."""
        return self._coda

    # -- Backwards-compatible accessors (deprecated) --

    @property
    def models(self) -> AsyncExtendedModelsClient:  # type: ignore[override]
        """**Deprecated.** Use ``client.control.models`` instead."""
        warnings.warn(
            "client.models is deprecated; use client.control.models instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self._control.models

    @property
    def model_results(self) -> AsyncModelResultsClient:  # type: ignore[override]
        """**Deprecated.** Use ``client.control.model_results`` instead."""
        warnings.warn(
            "client.model_results is deprecated; use client.control.model_results instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self._control.model_results

    # -- Top-level Coda shortcuts (no name conflicts) --

    async def health(self) -> dict[str, typing.Any]:
        """Shortcut for ``self.coda.health()``."""
        return await self._coda.health()

    async def transpile(self, *, source_code: str, target: str) -> dict[str, typing.Any]:
        """Shortcut for ``self.coda.transpile(...)``."""
        return await self._coda.transpile(source_code=source_code, target=target)

    async def simulate(
        self,
        *,
        code: str,
        method: str = "qasm",
        shots: int = 1024,
        seed_simulator: typing.Optional[int] = None,
        backend: str = "auto",
    ) -> dict[str, typing.Any]:
        """Shortcut for ``self.coda.simulate(...)``."""
        return await self._coda.simulate(
            code=code, method=method, shots=shots, seed_simulator=seed_simulator, backend=backend
        )

    async def to_openqasm3(self, *, code: str) -> dict[str, typing.Any]:
        """Shortcut for ``self.coda.to_openqasm3(...)``."""
        return await self._coda.to_openqasm3(code=code)

    async def estimate_resources(self, *, code: str) -> dict[str, typing.Any]:
        """Shortcut for ``self.coda.estimate_resources(...)``."""
        return await self._coda.estimate_resources(code=code)

    async def split_circuit(self, *, code: str) -> dict[str, typing.Any]:
        """Shortcut for ``self.coda.split_circuit(...)``."""
        return await self._coda.split_circuit(code=code)

    async def qpu_submit(
        self,
        *,
        code: str,
        source_framework: str,
        backend: str,
        shots: int = 100,
        accept_overage: bool = False,
        braket_execution_mode_hint: typing.Optional[str] = None,
    ) -> dict[str, typing.Any]:
        """Shortcut for ``self.coda.qpu_submit(...)``."""
        return await self._coda.qpu_submit(
            code=code,
            source_framework=source_framework,
            backend=backend,
            shots=shots,
            accept_overage=accept_overage,
            braket_execution_mode_hint=braket_execution_mode_hint,
        )

    async def qpu_status(self, *, job_id: str) -> dict[str, typing.Any]:
        """Shortcut for ``self.coda.qpu_status(...)``."""
        return await self._coda.qpu_status(job_id=job_id)

    async def qpu_devices(self) -> dict[str, typing.Any]:
        """Shortcut for ``self.coda.qpu_devices()``."""
        return await self._coda.qpu_devices()

    async def qpu_estimate_cost(
        self,
        *,
        code: str,
        source_framework: str,
        backend: str,
        shots: int = 100,
        braket_execution_mode_hint: typing.Optional[str] = None,
    ) -> dict[str, typing.Any]:
        """Shortcut for ``self.coda.qpu_estimate_cost(...)``."""
        return await self._coda.qpu_estimate_cost(
            code=code,
            source_framework=source_framework,
            backend=backend,
            shots=shots,
            braket_execution_mode_hint=braket_execution_mode_hint,
        )

    async def agents(
        self,
        *,
        messages: list[dict[str, str]],
        thread_id: typing.Optional[str] = None,
        fast: bool = False,
        mode: str = "build",
    ) -> AsyncIterator[dict[str, typing.Any]]:
        """Shortcut for ``self.coda.agents(...)``."""
        async for event in self._coda.agents(messages=messages, thread_id=thread_id, fast=fast, mode=mode):
            yield event
