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

        client.coda.tools.simulate(...)         # Coda — circuit tools
        client.coda.qpus.run(...)               # Coda — QPU submission
        client.coda.agents.run(...)             # Coda — AI agents
        client.control.models.run(...)          # Control — analysis models

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
        # TODO(v2): Remove deprecated client.models accessor
        warnings.warn(
            "client.models is deprecated; use client.control.models instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self._control.models

    @property
    def model_results(self) -> ModelResultsClient:  # type: ignore[override]
        """**Deprecated.** Use ``client.control.model_results`` instead."""
        # TODO(v2): Remove deprecated client.model_results accessor
        warnings.warn(
            "client.model_results is deprecated; use client.control.model_results instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self._control.model_results

    # -- Top-level Coda shortcuts (deprecated) --
    # TODO(v2): Remove all top-level Coda shortcuts below; use client.coda.tools.*, client.coda.qpus.*, client.coda.agents.*

    def health(self) -> dict[str, typing.Any]:
        """Shortcut for ``self.coda.health()``."""
        return self._coda.health()

    def transpile(self, *, source_code: str, target: str) -> dict[str, typing.Any]:
        # TODO(v2): Remove top-level shortcut client.transpile(); use client.coda.tools.transpile()
        warnings.warn(
            "client.transpile() is deprecated; use client.coda.tools.transpile() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self._coda.tools.transpile(source_code=source_code, target=target)

    def simulate(
        self,
        *,
        code: str,
        method: str = "qasm",
        shots: int = 1024,
        seed_simulator: typing.Optional[int] = None,
        backend: str = "auto",
    ) -> dict[str, typing.Any]:
        # TODO(v2): Remove top-level shortcut client.simulate(); use client.coda.tools.simulate()
        warnings.warn(
            "client.simulate() is deprecated; use client.coda.tools.simulate() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self._coda.tools.simulate(
            code=code, method=method, shots=shots, seed_simulator=seed_simulator, backend=backend
        )

    def to_openqasm3(self, *, code: str) -> dict[str, typing.Any]:
        # TODO(v2): Remove top-level shortcut client.to_openqasm3(); use client.coda.tools.to_openqasm3()
        warnings.warn(
            "client.to_openqasm3() is deprecated; use client.coda.tools.to_openqasm3() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self._coda.tools.to_openqasm3(code=code)

    def estimate_resources(self, *, code: str) -> dict[str, typing.Any]:
        # TODO(v2): Remove top-level shortcut client.estimate_resources(); use client.coda.tools.estimate_resources()
        warnings.warn(
            "client.estimate_resources() is deprecated; use client.coda.tools.estimate_resources() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self._coda.tools.estimate_resources(code=code)

    def split_circuit(self, *, code: str) -> dict[str, typing.Any]:
        # TODO(v2): Remove top-level shortcut client.split_circuit(); use client.coda.tools.split_circuit()
        warnings.warn(
            "client.split_circuit() is deprecated; use client.coda.tools.split_circuit() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self._coda.tools.split_circuit(code=code)

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
        # TODO(v2): Remove top-level shortcut client.qpu_submit(); use client.coda.qpus.run()
        warnings.warn(
            "client.qpu_submit() is deprecated; use client.coda.qpus.run() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self._coda.qpus.run(
            code=code,
            source_framework=source_framework,
            backend=backend,
            shots=shots,
            accept_overage=accept_overage,
            braket_execution_mode_hint=braket_execution_mode_hint,
        )

    def qpu_status(self, *, job_id: str) -> dict[str, typing.Any]:
        # TODO(v2): Remove top-level shortcut client.qpu_status(); use client.coda.qpus.status()
        warnings.warn(
            "client.qpu_status() is deprecated; use client.coda.qpus.status() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self._coda.qpus.status(job_id=job_id)

    def qpu_devices(self) -> dict[str, typing.Any]:
        # TODO(v2): Remove top-level shortcut client.qpu_devices(); use client.coda.qpus.list()
        warnings.warn(
            "client.qpu_devices() is deprecated; use client.coda.qpus.list() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self._coda.qpus.list()

    def qpu_estimate_cost(
        self,
        *,
        code: str,
        source_framework: str,
        backend: str,
        shots: int = 100,
        braket_execution_mode_hint: typing.Optional[str] = None,
    ) -> dict[str, typing.Any]:
        # TODO(v2): Remove top-level shortcut client.qpu_estimate_cost(); use client.coda.qpus.estimate_cost()
        warnings.warn(
            "client.qpu_estimate_cost() is deprecated; use client.coda.qpus.estimate_cost() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self._coda.qpus.estimate_cost(
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
        # TODO(v2): Remove top-level shortcut client.agents(); use client.coda.agents.run()
        warnings.warn(
            "client.agents() is deprecated; use client.coda.agents.run() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self._coda.agents.run(messages=messages, thread_id=thread_id, fast=fast, mode=mode)

    def agents_list(self) -> dict[str, typing.Any]:
        # TODO(v2): Remove top-level shortcut client.agents_list(); use client.coda.agents.list()
        warnings.warn(
            "client.agents_list() is deprecated; use client.coda.agents.list() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self._coda.agents.list()


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
        # TODO(v2): Remove deprecated client.models accessor
        warnings.warn(
            "client.models is deprecated; use client.control.models instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self._control.models

    @property
    def model_results(self) -> AsyncModelResultsClient:  # type: ignore[override]
        """**Deprecated.** Use ``client.control.model_results`` instead."""
        # TODO(v2): Remove deprecated client.model_results accessor
        warnings.warn(
            "client.model_results is deprecated; use client.control.model_results instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self._control.model_results

    # -- Top-level Coda shortcuts (deprecated) --
    # TODO(v2): Remove all top-level async Coda shortcuts below

    async def health(self) -> dict[str, typing.Any]:
        """Shortcut for ``self.coda.health()``."""
        return await self._coda.health()

    async def transpile(self, *, source_code: str, target: str) -> dict[str, typing.Any]:
        # TODO(v2): Remove top-level shortcut
        warnings.warn(
            "client.transpile() is deprecated; use client.coda.tools.transpile() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return await self._coda.tools.transpile(source_code=source_code, target=target)

    async def simulate(
        self,
        *,
        code: str,
        method: str = "qasm",
        shots: int = 1024,
        seed_simulator: typing.Optional[int] = None,
        backend: str = "auto",
    ) -> dict[str, typing.Any]:
        # TODO(v2): Remove top-level shortcut
        warnings.warn(
            "client.simulate() is deprecated; use client.coda.tools.simulate() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return await self._coda.tools.simulate(
            code=code, method=method, shots=shots, seed_simulator=seed_simulator, backend=backend
        )

    async def to_openqasm3(self, *, code: str) -> dict[str, typing.Any]:
        # TODO(v2): Remove top-level shortcut
        warnings.warn(
            "client.to_openqasm3() is deprecated; use client.coda.tools.to_openqasm3() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return await self._coda.tools.to_openqasm3(code=code)

    async def estimate_resources(self, *, code: str) -> dict[str, typing.Any]:
        # TODO(v2): Remove top-level shortcut
        warnings.warn(
            "client.estimate_resources() is deprecated; use client.coda.tools.estimate_resources() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return await self._coda.tools.estimate_resources(code=code)

    async def split_circuit(self, *, code: str) -> dict[str, typing.Any]:
        # TODO(v2): Remove top-level shortcut
        warnings.warn(
            "client.split_circuit() is deprecated; use client.coda.tools.split_circuit() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return await self._coda.tools.split_circuit(code=code)

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
        # TODO(v2): Remove top-level shortcut
        warnings.warn(
            "client.qpu_submit() is deprecated; use client.coda.qpus.run() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return await self._coda.qpus.run(
            code=code,
            source_framework=source_framework,
            backend=backend,
            shots=shots,
            accept_overage=accept_overage,
            braket_execution_mode_hint=braket_execution_mode_hint,
        )

    async def qpu_status(self, *, job_id: str) -> dict[str, typing.Any]:
        # TODO(v2): Remove top-level shortcut
        warnings.warn(
            "client.qpu_status() is deprecated; use client.coda.qpus.status() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return await self._coda.qpus.status(job_id=job_id)

    async def qpu_devices(self) -> dict[str, typing.Any]:
        # TODO(v2): Remove top-level shortcut
        warnings.warn(
            "client.qpu_devices() is deprecated; use client.coda.qpus.list() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return await self._coda.qpus.list()

    async def qpu_estimate_cost(
        self,
        *,
        code: str,
        source_framework: str,
        backend: str,
        shots: int = 100,
        braket_execution_mode_hint: typing.Optional[str] = None,
    ) -> dict[str, typing.Any]:
        # TODO(v2): Remove top-level shortcut
        warnings.warn(
            "client.qpu_estimate_cost() is deprecated; use client.coda.qpus.estimate_cost() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return await self._coda.qpus.estimate_cost(
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
        # TODO(v2): Remove top-level shortcut
        warnings.warn(
            "client.agents() is deprecated; use client.coda.agents.run() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        async for event in self._coda.agents.run(messages=messages, thread_id=thread_id, fast=fast, mode=mode):
            yield event

    async def agents_list(self) -> dict[str, typing.Any]:
        # TODO(v2): Remove top-level shortcut
        warnings.warn(
            "client.agents_list() is deprecated; use client.coda.agents.list() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return await self._coda.agents.list()
