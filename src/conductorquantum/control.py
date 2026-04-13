"""Control API namespace — groups models and model_results under client.control.

This provides the preferred access path that mirrors the product structure
(Coda vs Control). The legacy ``client.models`` and ``client.model_results``
accessors inherited from the Fern-generated base class still work and point
to the same objects. Once ``client.control`` is established as the canonical
path, the legacy accessors will be deprecated and eventually removed in a
future major version.

Deprecation plan:
  1. (current) Both paths work, docs prefer ``client.control.*``.
  2. (future) Add ``DeprecationWarning`` to ``client.models`` / ``client.model_results``.
  3. (major version) Remove the legacy accessors from the base class override.
"""

from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    from conductorquantum.model_results.client import AsyncModelResultsClient, ModelResultsClient
    from conductorquantum.models.extended_client import AsyncExtendedModelsClient, ExtendedModelsClient


class ControlClient:
    """Namespace for the Control product line (models + model results).

    Accessed via ``ConductorQuantum(...).control``. This is the preferred path;
    ``client.models`` and ``client.model_results`` still work for backwards
    compatibility but will be deprecated in a future version.
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
    path; ``client.models`` and ``client.model_results`` still work for
    backwards compatibility but will be deprecated in a future version.
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
