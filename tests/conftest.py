import os

import pytest
from conductorquantum import AsyncConductorQuantum, ConductorQuantum

API_BASE_URL = os.environ.get("API_BASE_URL", "https://api.conductorquantum.com/v0")


def _env(name: str) -> str | None:
    val = os.environ.get(name)
    return val if val else None


# ---------------------------------------------------------------------------
# Token fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def coda_api_key() -> str | None:
    return _env("CODA_API_TOKEN") or _env("CONDUCTOR_QUANTUM_API_KEY")


@pytest.fixture(scope="session")
def control_api_key() -> str | None:
    return _env("CONTROL_API_TOKEN") or _env("CONDUCTOR_QUANTUM_API_KEY")


@pytest.fixture(scope="session")
def api_key(control_api_key: str | None, coda_api_key: str | None) -> str:
    """Backward-compat fixture: returns *any* available token (preferring control)."""
    key = control_api_key or coda_api_key
    if key is None:
        pytest.skip("Set CONTROL_API_TOKEN / CODA_API_TOKEN / CONDUCTOR_QUANTUM_API_KEY")
    return key


@pytest.fixture(scope="session")
def client(api_key: str) -> ConductorQuantum:
    return ConductorQuantum(token=api_key, base_url=API_BASE_URL)


@pytest.fixture(scope="session")
def coda_client(coda_api_key: str | None) -> ConductorQuantum:
    """Session-scoped sync client wired for **Coda** only."""
    if coda_api_key is None:
        pytest.skip("Set CODA_API_TOKEN or CONDUCTOR_QUANTUM_API_KEY")
    return ConductorQuantum(token=coda_api_key, base_url=API_BASE_URL)


@pytest.fixture()
def async_client(api_key: str) -> AsyncConductorQuantum:
    return AsyncConductorQuantum(token=api_key, base_url=API_BASE_URL)


@pytest.fixture()
def async_coda_client(coda_api_key: str | None) -> AsyncConductorQuantum:
    """Function-scoped async client wired for **Coda** only."""
    if coda_api_key is None:
        pytest.skip("Set CODA_API_TOKEN or CONDUCTOR_QUANTUM_API_KEY")
    return AsyncConductorQuantum(token=coda_api_key, base_url=API_BASE_URL)
