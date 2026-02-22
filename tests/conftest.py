import os
from pathlib import Path

import pytest

from conductorquantum import AsyncConductorQuantum, ConductorQuantum

API_BASE_URL = "https://api.conductorquantum.com/v0"

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures" / "example_inputs"


def _get_api_key() -> str | None:
    return os.environ.get("CONDUCTOR_QUANTUM_API_KEY")


@pytest.fixture(scope="session")
def api_key() -> str:
    key = _get_api_key()
    if key is None:
        pytest.skip("CONDUCTOR_QUANTUM_API_KEY environment variable not set")
    return key


@pytest.fixture(scope="session")
def client(api_key: str) -> ConductorQuantum:
    return ConductorQuantum(token=api_key, base_url=API_BASE_URL)


@pytest.fixture(scope="session")
def async_client(api_key: str) -> AsyncConductorQuantum:
    return AsyncConductorQuantum(token=api_key, base_url=API_BASE_URL)


@pytest.fixture(scope="session")
def available_model_ids() -> list[str]:
    if not FIXTURES_DIR.exists():
        pytest.skip(f"Fixtures directory not found: {FIXTURES_DIR}")
    ids = [p.stem for p in sorted(FIXTURES_DIR.glob("*.npy"))]
    if not ids:
        pytest.skip("No example input fixture files found")
    return ids
