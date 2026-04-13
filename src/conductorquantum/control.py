"""Control API namespace — groups models and model_results under client.control.

This provides the preferred access path that mirrors the product structure
(Coda vs Control). The legacy ``client.models`` and ``client.model_results``
accessors inherited from the Fern-generated base class still work and point
to the same objects but emit ``DeprecationWarning``.

Deprecation status:
  1. (done)    Both paths work, docs prefer ``client.control.*``.
  2. (done)    ``DeprecationWarning`` emitted by ``client.models`` / ``client.model_results``.
  3. (planned) Remove the legacy accessors in a future major version.
"""

from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    from conductorquantum.model_results.client import AsyncModelResultsClient, ModelResultsClient
    from conductorquantum.models.extended_client import AsyncExtendedModelsClient, ExtendedModelsClient


class ControlClient:
    """Namespace for the Control product line (models + model results).

    Accessed via ``ConductorQuantum(...).control``. This is the preferred path;
    ``client.models`` and ``client.model_results`` still work but emit
    ``DeprecationWarning`` and will be removed in a future major version.
    """

    def __init__(
        self,
        *,
        models: ExtendedModelsClient,
        model_results: ModelResultsClient,
    ) -> None:
        self._models = models
        self._model_results = model_results

    @property
    def models(self) -> ExtendedModelsClient:
        return self._models

    @property
    def model_results(self) -> ModelResultsClient:
        return self._model_results


class AsyncControlClient:
    """Async namespace for the Control product line (models + model results).

    Accessed via ``AsyncConductorQuantum(...).control``. This is the preferred
    path; ``client.models`` and ``client.model_results`` still work but emit
    ``DeprecationWarning`` and will be removed in a future major version.
    """

    def __init__(
        self,
        *,
        models: AsyncExtendedModelsClient,
        model_results: AsyncModelResultsClient,
    ) -> None:
        self._models = models
        self._model_results = model_results

    @property
    def models(self) -> AsyncExtendedModelsClient:
        return self._models

    @property
    def model_results(self) -> AsyncModelResultsClient:
        return self._model_results
