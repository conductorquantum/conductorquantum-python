from __future__ import annotations

import datetime as dt

import httpx
import numpy as np

from conductorquantum import AsyncConductorQuantum, ConductorQuantum, ModelBatchResultPublic

BASE_URL = "https://api.example.test/v0/control"
TOKEN = "test-token"
MODEL = "coulomb-blockade-peak-detector-v2"


def _batch_response() -> dict[str, object]:
    return {
        "id": "batch-result-id",
        "created_at": "2026-05-13T19:00:00Z",
        "input_file_name": "batch.npy",
        "model": MODEL,
        "batch_size": 2,
        "output": {
            "outputs": [
                {"peak_indices": [1, 3]},
                {"peak_indices": [2, 4]},
            ]
        },
    }


def test_models_batch_run_posts_single_multipart_file() -> None:
    captured_requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured_requests.append(request)
        body = request.read()
        assert request.method == "POST"
        assert str(request.url) == f"{BASE_URL}/models/batch"
        assert request.headers["authorization"] == f"Bearer {TOKEN}"
        assert b'name="model"' in body
        assert MODEL.encode() in body
        assert b'name="data"' in body
        return httpx.Response(200, json=_batch_response())

    client = ConductorQuantum(
        token=TOKEN,
        base_url=BASE_URL,
        httpx_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    result = client.control.models.batch.run(
        model=MODEL,
        data=np.zeros((2, 128), dtype=np.float32),
    )

    assert len(captured_requests) == 1
    assert isinstance(result, ModelBatchResultPublic)
    assert result.id == "batch-result-id"
    assert result.model == MODEL
    assert result.batch_size == 2
    assert result.input_file_name == "batch.npy"
    assert not hasattr(result, "input_file_size")
    assert result.created_at == dt.datetime(2026, 5, 13, 19, 0, tzinfo=dt.timezone.utc)
    assert result.output["outputs"] == [{"peak_indices": [1, 3]}, {"peak_indices": [2, 4]}]


async def test_async_models_batch_run_posts_single_multipart_file() -> None:
    captured_requests: list[httpx.Request] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        captured_requests.append(request)
        body = await request.aread()
        assert request.method == "POST"
        assert str(request.url) == f"{BASE_URL}/models/batch"
        assert request.headers["authorization"] == f"Bearer {TOKEN}"
        assert b'name="model"' in body
        assert MODEL.encode() in body
        assert b'name="data"' in body
        return httpx.Response(200, json=_batch_response())

    client = AsyncConductorQuantum(
        token=TOKEN,
        base_url=BASE_URL,
        httpx_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
    )

    result = await client.control.models.batch.run(
        model=MODEL,
        data=np.zeros((2, 128), dtype=np.float32),
    )

    assert len(captured_requests) == 1
    assert isinstance(result, ModelBatchResultPublic)
    assert result.batch_size == 2
    assert result.input_file_name == "batch.npy"
    assert not hasattr(result, "input_file_size")
    assert result.output["outputs"] == [{"peak_indices": [1, 3]}, {"peak_indices": [2, 4]}]
