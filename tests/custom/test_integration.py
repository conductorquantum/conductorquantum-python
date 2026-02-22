"""Integration tests for the ConductorQuantum Python client.

These tests run against the live API at https://api.conductorquantum.com/v0
and require a valid API key set via the CONDUCTOR_QUANTUM_API_KEY environment variable.

Example numpy input files are bundled under tests/fixtures/example_inputs/.

Usage:
    CONDUCTOR_QUANTUM_API_KEY=<key> pytest tests/custom/test_integration.py -v
    CONDUCTOR_QUANTUM_API_KEY=<key> pytest tests/custom/test_integration.py -v -k "TestModelsExecute"
"""

from __future__ import annotations

import io
import os
import zipfile
from pathlib import Path

import numpy as np
import pytest

from conductorquantum import (
    AsyncConductorQuantum,
    ConductorQuantum,
    ModelPublic,
    ModelResultPublic,
    ModelResultPublicMasked,
    NotFoundError,
)

FIXTURES_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "example_inputs"

MODEL_EXAMPLE_INPUTS: dict[str, str] = {
    # Coulomb blockade classifiers
    "coulomb-blockade-classifier-v0": "coulomb-blockade-classifier-v0.npy",
    "coulomb-blockade-classifier-v1": "coulomb-blockade-classifier-v1.npy",
    "coulomb-blockade-classifier-v2": "coulomb-blockade-classifier-v2.npy",
    "coulomb-blockade-classifier-v3": "coulomb-blockade-classifier-v3.npy",
    # Coulomb blockade peak detectors
    "coulomb-blockade-peak-detector-v0": "coulomb-blockade-peak-detector-v0.npy",
    "coulomb-blockade-peak-detector-v1": "coulomb-blockade-peak-detector-v1.npy",
    "coulomb-blockade-peak-detector-v1-mini": "coulomb-blockade-peak-detector-v1-mini.npy",
    "coulomb-blockade-peak-detector-v2": "coulomb-blockade-peak-detector-v2.npy",
    # Pinch-off
    "pinch-off-classifier-v0": "pinch-off-classifier-v0.npy",
    "pinch-off-parameter-extractor-v0": "pinch-off-parameter-extractor-v0.npy",
    # Turn-on
    "turn-on-classifier-v0": "turn-on-classifier-v0.npy",
    "turn-on-parameter-extractor-v0": "turn-on-parameter-extractor-v0.npy",
    # CSD classifiers
    "charge-stability-diagram-binary-classifier-v0-16x16": "charge-stability-diagram-binary-classifier-v0-16x16.npy",
    "charge-stability-diagram-binary-classifier-v1-16x16": "charge-stability-diagram-binary-classifier-v1-16x16.npy",
    "charge-stability-diagram-binary-classifier-v2-16x16": "charge-stability-diagram-binary-classifier-v2-16x16.npy",
    "charge-stability-diagram-binary-classifier-v3-16x16": "charge-stability-diagram-binary-classifier-v3-16x16.npy",
    "charge-stability-diagram-binary-classifier-v0-48x48": "charge-stability-diagram-binary-classifier-v0-48x48.npy",
    "charge-stability-diagram-binary-classifier-v1-48x48": "charge-stability-diagram-binary-classifier-v1-48x48.npy",
    # CSD transition detectors
    "charge-stability-diagram-transition-detector-v0": "charge-stability-diagram-transition-detector-v0.npy",
    "charge-stability-diagram-transition-detector-v1": "charge-stability-diagram-transition-detector-v1.npy",
    "charge-stability-diagram-transition-detector-v2": "charge-stability-diagram-transition-detector-v2.npy",
    "charge-stability-diagram-transition-detector-v3": "charge-stability-diagram-transition-detector-v3.npy",
    # CSD segmenter
    "charge-stability-diagram-segmenter-v0": "charge-stability-diagram-segmenter-v0.npy",
    # Coulomb diamond
    "coulomb-diamond-detector-v0": "coulomb-diamond-detector-v0.npy",
    "coulomb-diamond-detector-v1": "coulomb-diamond-detector-v1.npy",
    "coulomb-diamond-segmenter-v0": "coulomb-diamond-segmenter-v0.npy",
    # Electron unload
    "electron-unload-detector-v0": "electron-unload-detector-v0.npy",
    "electron-unload-texture-detector-v0": "electron-unload-texture-detector-v0.npy",
    # Anticrossing
    "anticrossing-detector-v0": "anticrossing-detector-v0.npy",
}

MODEL_EXPECTED_OUTPUT_KEYS: dict[str, set[str]] = {
    "coulomb-blockade-classifier-v0": {"classification"},
    "coulomb-blockade-classifier-v1": {"classification"},
    "coulomb-blockade-classifier-v2": {"classification", "score"},
    "coulomb-blockade-classifier-v3": {"classification", "score"},
    "coulomb-blockade-peak-detector-v0": {"peak_indices"},
    "coulomb-blockade-peak-detector-v1": {"peak_indices"},
    "coulomb-blockade-peak-detector-v1-mini": {"peak_indices"},
    "coulomb-blockade-peak-detector-v2": {"peak_indices"},
    "pinch-off-classifier-v0": {"classification"},
    "pinch-off-parameter-extractor-v0": {"cut_off_index", "transition_index", "saturation_index"},
    "turn-on-classifier-v0": {"classification"},
    "turn-on-parameter-extractor-v0": {"threshold_idx"},
    "charge-stability-diagram-binary-classifier-v0-16x16": {"classification", "score"},
    "charge-stability-diagram-binary-classifier-v1-16x16": {"classification", "score"},
    "charge-stability-diagram-binary-classifier-v2-16x16": {"classification", "score"},
    "charge-stability-diagram-binary-classifier-v3-16x16": {"classification", "score"},
    "charge-stability-diagram-binary-classifier-v0-48x48": {"classification", "score"},
    "charge-stability-diagram-binary-classifier-v1-48x48": {"classification", "score"},
    "charge-stability-diagram-transition-detector-v0": {"transition_lines"},
    "charge-stability-diagram-transition-detector-v1": {"transition_lines"},
    "charge-stability-diagram-transition-detector-v2": {"transition_lines"},
    "charge-stability-diagram-transition-detector-v3": {"transition_lines"},
    "charge-stability-diagram-segmenter-v0": {"segmentation"},
    "coulomb-diamond-detector-v0": {"diamond_vertices"},
    "coulomb-diamond-detector-v1": {"diamond_vertices"},
    "coulomb-diamond-segmenter-v0": {"segmentation"},
    "electron-unload-detector-v0": {"unload_indices"},
    "electron-unload-texture-detector-v0": {"texture_clusters"},
    "anticrossing-detector-v0": set(),
}

_skip_no_key = pytest.mark.skipif(
    os.environ.get("CONDUCTOR_QUANTUM_API_KEY") is None,
    reason="CONDUCTOR_QUANTUM_API_KEY environment variable not set",
)

pytestmark = [_skip_no_key, pytest.mark.integration]


def _load_example(model_id: str) -> np.ndarray:
    return np.load(FIXTURES_DIR / MODEL_EXAMPLE_INPUTS[model_id])


# ---------------------------------------------------------------------------
# Models API
# ---------------------------------------------------------------------------


class TestModelsList:
    def test_returns_non_empty_list(self, client: ConductorQuantum) -> None:
        models = client.models.list()
        assert isinstance(models, list)
        assert len(models) > 0

    def test_each_item_is_model_public(self, client: ConductorQuantum) -> None:
        models = client.models.list(limit=5)
        for m in models:
            assert isinstance(m, ModelPublic)
            assert m.id
            assert m.name
            assert m.description
            assert m.released is not None
            assert m.number_of_runs >= 0
            assert m.input_shape_requirements

    def test_pagination_skip_and_limit(self, client: ConductorQuantum) -> None:
        all_models = client.models.list()
        if len(all_models) < 2:
            pytest.skip("Not enough models to test pagination")

        first = client.models.list(limit=1)
        assert len(first) == 1

        second = client.models.list(skip=1, limit=1)
        assert len(second) == 1
        assert first[0].id != second[0].id


class TestModelsInfo:
    def test_returns_model_details(self, client: ConductorQuantum) -> None:
        models = client.models.list(limit=1)
        model_id = models[0].id

        info = client.models.info(model_id)
        assert isinstance(info, ModelPublic)
        assert info.id == model_id
        assert info.name == models[0].name

    def test_known_model_ids(self, client: ConductorQuantum, available_model_ids: list[str]) -> None:
        for model_id in available_model_ids:
            info = client.models.info(model_id)
            assert info.id == model_id

    def test_not_found_raises(self, client: ConductorQuantum) -> None:
        with pytest.raises(NotFoundError):
            client.models.info("nonexistent-model-that-does-not-exist")


class TestModelsExecute:
    """Test model execution with real example numpy inputs.

    Each model is tested with its corresponding example_input.npy fixture,
    verifying the response structure and output keys.
    """

    @pytest.fixture(params=list(MODEL_EXAMPLE_INPUTS.keys()))
    def model_id(self, request: pytest.FixtureRequest) -> str:
        mid = request.param
        if not (FIXTURES_DIR / MODEL_EXAMPLE_INPUTS[mid]).exists():
            pytest.skip(f"Fixture not found for {mid}")
        return mid

    def test_execute_returns_result(
        self,
        client: ConductorQuantum,
        model_id: str,
    ) -> None:
        data = _load_example(model_id)
        assert isinstance(data, np.ndarray)

        result = client.models.execute(model=model_id, data=data)

        assert isinstance(result, ModelResultPublic)
        assert result.id
        assert result.model == model_id
        assert result.created_at is not None
        assert result.input_file_name
        assert result.input_file_size > 0
        assert isinstance(result.output, dict)

    def test_output_contains_expected_keys(
        self,
        client: ConductorQuantum,
        model_id: str,
    ) -> None:
        data = _load_example(model_id)
        result = client.models.execute(model=model_id, data=data)

        expected_keys = MODEL_EXPECTED_OUTPUT_KEYS.get(model_id)
        if expected_keys is not None and len(expected_keys) > 0:
            assert expected_keys.issubset(result.output.keys()), (
                f"Missing keys for {model_id}: expected {expected_keys}, got {set(result.output.keys())}"
            )

    def test_execute_with_file_object(
        self,
        client: ConductorQuantum,
        available_model_ids: list[str],
    ) -> None:
        """Verify execute works when passing a file object instead of np.ndarray."""
        model_id = available_model_ids[0]
        fixture_path = FIXTURES_DIR / MODEL_EXAMPLE_INPUTS[model_id]

        with open(fixture_path, "rb") as f:
            result = client.models.execute(model=model_id, data=f)

        assert isinstance(result, ModelResultPublic)
        assert result.model == model_id

    def test_execute_not_found_model(self, client: ConductorQuantum, available_model_ids: list[str]) -> None:
        model_id = available_model_ids[0]
        data = _load_example(model_id)

        with pytest.raises(NotFoundError):
            client.models.execute(model="nonexistent-model-xyz", data=data)


# ---------------------------------------------------------------------------
# Model Results API
# ---------------------------------------------------------------------------


class TestModelResultsList:
    def test_returns_list(self, client: ConductorQuantum) -> None:
        results = client.model_results.list(limit=5)
        assert isinstance(results, list)
        for r in results:
            assert isinstance(r, ModelResultPublicMasked)
            assert r.id
            assert r.model
            assert r.created_at is not None
            assert isinstance(r.output, dict)

    def test_pagination(self, client: ConductorQuantum) -> None:
        page1 = client.model_results.list(limit=2)
        if len(page1) < 2:
            pytest.skip("Not enough results to test pagination")

        page2 = client.model_results.list(skip=1, limit=1)
        assert len(page2) == 1
        assert page1[1].id == page2[0].id


class TestModelResultsLifecycle:
    """Test the full lifecycle: execute -> info -> download -> delete."""

    @pytest.fixture()
    def executed_result(
        self,
        client: ConductorQuantum,
        available_model_ids: list[str],
    ) -> ModelResultPublic:
        model_id = available_model_ids[0]
        data = _load_example(model_id)
        return client.models.execute(model=model_id, data=data)

    def test_info_returns_full_result(
        self,
        client: ConductorQuantum,
        executed_result: ModelResultPublic,
    ) -> None:
        info = client.model_results.info(executed_result.id)
        assert isinstance(info, ModelResultPublic)
        assert info.id == executed_result.id
        assert info.model == executed_result.model
        assert info.output == executed_result.output
        assert info.input_file_name == executed_result.input_file_name
        assert info.input_file_size == executed_result.input_file_size

    def test_download_returns_valid_zip(
        self,
        client: ConductorQuantum,
        executed_result: ModelResultPublic,
    ) -> None:
        chunks = list(client.model_results.download(executed_result.id))
        assert len(chunks) > 0

        content = b"".join(chunks)
        assert len(content) > 0

        buf = io.BytesIO(content)
        assert zipfile.is_zipfile(buf)

        buf.seek(0)
        with zipfile.ZipFile(buf) as zf:
            names = zf.namelist()
            assert len(names) >= 1

    def test_delete_removes_result(
        self,
        client: ConductorQuantum,
        executed_result: ModelResultPublic,
    ) -> None:
        client.model_results.delete(executed_result.id)

        with pytest.raises(NotFoundError):
            client.model_results.info(executed_result.id)


class TestModelResultsNotFound:
    def test_info_not_found(self, client: ConductorQuantum) -> None:
        with pytest.raises(NotFoundError):
            client.model_results.info("00000000-0000-0000-0000-000000000000")

    def test_download_not_found(self, client: ConductorQuantum) -> None:
        with pytest.raises(NotFoundError):
            list(client.model_results.download("00000000-0000-0000-0000-000000000000"))

    def test_delete_not_found(self, client: ConductorQuantum) -> None:
        with pytest.raises(NotFoundError):
            client.model_results.delete("00000000-0000-0000-0000-000000000000")


# ---------------------------------------------------------------------------
# Async Client
# ---------------------------------------------------------------------------


class TestAsyncModels:
    async def test_list(self, async_client: AsyncConductorQuantum) -> None:
        models = await async_client.models.list(limit=3)
        assert isinstance(models, list)
        assert len(models) > 0
        for m in models:
            assert isinstance(m, ModelPublic)

    async def test_info(self, async_client: AsyncConductorQuantum) -> None:
        models = await async_client.models.list(limit=1)
        info = await async_client.models.info(models[0].id)
        assert info.id == models[0].id

    async def test_execute(
        self,
        async_client: AsyncConductorQuantum,
        available_model_ids: list[str],
    ) -> None:
        model_id = available_model_ids[0]
        data = _load_example(model_id)

        result = await async_client.models.execute(model=model_id, data=data)
        assert isinstance(result, ModelResultPublic)
        assert result.model == model_id
        assert isinstance(result.output, dict)


class TestAsyncModelResults:
    async def test_list(self, async_client: AsyncConductorQuantum) -> None:
        results = await async_client.model_results.list(limit=3)
        assert isinstance(results, list)
        for r in results:
            assert isinstance(r, ModelResultPublicMasked)

    async def test_lifecycle(
        self,
        async_client: AsyncConductorQuantum,
        available_model_ids: list[str],
    ) -> None:
        """Execute -> info -> delete via async client."""
        model_id = available_model_ids[0]
        data = _load_example(model_id)

        result = await async_client.models.execute(model=model_id, data=data)
        assert isinstance(result, ModelResultPublic)

        info = await async_client.model_results.info(result.id)
        assert info.id == result.id

        await async_client.model_results.delete(result.id)

        with pytest.raises(NotFoundError):
            await async_client.model_results.info(result.id)
