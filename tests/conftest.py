import os

import pytest

from conductorquantum import AsyncConductorQuantum, ConductorQuantum

API_BASE_URL = "https://api.conductorquantum.com/v0"


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


@pytest.fixture()
def async_client(api_key: str) -> AsyncConductorQuantum:
    return AsyncConductorQuantum(token=api_key, base_url=API_BASE_URL)
