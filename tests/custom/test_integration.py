"""Integration tests for the ConductorQuantum Python client.

These tests run against the live API at https://api.conductorquantum.com/v0
and require a valid API key set via the CONDUCTOR_QUANTUM_API_KEY environment variable.

Mock numpy arrays are generated inline with the correct shapes for each model.
See https://docs.conductorquantum.com/models/getting-started/overview for
the model catalogue, expected input shapes, and output keys.

Usage:
    CONDUCTOR_QUANTUM_API_KEY=<key> pytest tests/custom/test_integration.py -v
    CONDUCTOR_QUANTUM_API_KEY=<key> pytest tests/custom/test_integration.py -v -k "TestModelsExecute"
"""

from __future__ import annotations

import io
import os
import tempfile
import zipfile

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

# Maps each model ID to the numpy array shape it expects.
# Shapes taken from https://docs.conductorquantum.com/models/getting-started/overview
MODEL_INPUT_SHAPES: dict[str, tuple[int, ...]] = {
    # Coulomb blockade classifiers
    "coulomb-blockade-classifier-v0": (100,),
    "coulomb-blockade-classifier-v1": (100,),
    "coulomb-blockade-classifier-v2": (128,),
    "coulomb-blockade-classifier-v3": (128,),
    # Coulomb blockade peak detectors
    "coulomb-blockade-peak-detector-v0": (100,),
    "coulomb-blockade-peak-detector-v1": (500,),
    "coulomb-blockade-peak-detector-v1-mini": (500,),
    "coulomb-blockade-peak-detector-v2": (128,),
    # Pinch-off
    "pinch-off-classifier-v0": (100,),
    "pinch-off-parameter-extractor-v0": (100,),
    # Turn-on
    "turn-on-classifier-v0": (100,),
    "turn-on-parameter-extractor-v0": (100,),
    # CSD binary classifiers
    "charge-stability-diagram-binary-classifier-v0-16x16": (16, 16),
    "charge-stability-diagram-binary-classifier-v1-16x16": (16, 16),
    "charge-stability-diagram-binary-classifier-v2-16x16": (16, 16),
    "charge-stability-diagram-binary-classifier-v3-16x16": (16, 16),
    "charge-stability-diagram-binary-classifier-v0-48x48": (48, 48),
    "charge-stability-diagram-binary-classifier-v1-48x48": (48, 48),
    # CSD transition detectors
    "charge-stability-diagram-transition-detector-v0": (128, 128),
    "charge-stability-diagram-transition-detector-v1": (128, 128),
    "charge-stability-diagram-transition-detector-v2": (128, 128),
    "charge-stability-diagram-transition-detector-v3": (128, 128),
    # CSD segmenter
    "charge-stability-diagram-segmenter-v0": (128, 128),
    # Coulomb diamond
    "coulomb-diamond-detector-v0": (256, 256),
    "coulomb-diamond-detector-v1": (128, 128),
    "coulomb-diamond-segmenter-v0": (128, 128),
    # Electron unload
    "electron-unload-detector-v0": (101, 51),
    "electron-unload-texture-detector-v0": (101, 51),
    # Anticrossing
    "anticrossing-detector-v0": (2, 801, 127),
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
    "turn-on-parameter-extractor-v0": {"threshold_index"},
    "charge-stability-diagram-binary-classifier-v0-16x16": {"classification"},
    "charge-stability-diagram-binary-classifier-v1-16x16": {"classification"},
    "charge-stability-diagram-binary-classifier-v2-16x16": {"classification"},
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


def _generate_example(model_id: str) -> np.ndarray:
    """Generate a deterministic random numpy array with the correct shape for *model_id*."""
    rng = np.random.default_rng(42)
    return rng.random(MODEL_INPUT_SHAPES[model_id])


@pytest.fixture(scope="session")
def available_model_ids() -> list[str]:
    return list(MODEL_INPUT_SHAPES.keys())


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
    """Test model execution with a single generated mock numpy input.

    Uses one representative model to verify the positive and negative paths
    without hitting every model endpoint (which would be too slow for CI).
    """

    SAMPLE_MODEL = "coulomb-blockade-classifier-v0"

    def test_execute_returns_result(self, client: ConductorQuantum) -> None:
        model_id = self.SAMPLE_MODEL
        data = _generate_example(model_id)
        assert isinstance(data, np.ndarray)

        result = client.models.execute(model=model_id, data=data)

        assert isinstance(result, ModelResultPublic)
        assert result.id
        assert result.model == model_id
        assert result.created_at is not None
        assert result.input_file_name
        assert result.input_file_size > 0
        assert isinstance(result.output, dict)

        expected_keys = MODEL_EXPECTED_OUTPUT_KEYS[model_id]
        assert expected_keys.issubset(result.output.keys()), (
            f"Missing keys for {model_id}: expected {expected_keys}, got {set(result.output.keys())}"
        )

    def test_execute_with_file_object(self, client: ConductorQuantum) -> None:
        """Verify execute works when passing a file object instead of np.ndarray."""
        model_id = self.SAMPLE_MODEL
        data = _generate_example(model_id)

        with tempfile.NamedTemporaryFile(suffix=".npy", delete=False) as tmp:
            np.save(tmp, data)
            tmp_path = tmp.name

        try:
            with open(tmp_path, "rb") as f:
                result = client.models.execute(model=model_id, data=f)

            assert isinstance(result, ModelResultPublic)
            assert result.model == model_id
        finally:
            os.unlink(tmp_path)

    def test_execute_not_found_model(self, client: ConductorQuantum) -> None:
        model_id = self.SAMPLE_MODEL
        data = _generate_example(model_id)

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
        data = _generate_example(model_id)
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
        assert info.input_file_size > 0

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
        data = _generate_example(model_id)

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
        data = _generate_example(model_id)

        result = await async_client.models.execute(model=model_id, data=data)
        assert isinstance(result, ModelResultPublic)

        info = await async_client.model_results.info(result.id)
        assert info.id == result.id

        await async_client.model_results.delete(result.id)

        with pytest.raises(NotFoundError):
            await async_client.model_results.info(result.id)
