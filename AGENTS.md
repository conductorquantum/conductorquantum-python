# AGENTS.md

## Cursor Cloud specific instructions

This is a Python SDK client library (not a runnable application). There are no services to start — the SDK talks to remote Conductor Quantum APIs.

### Quick reference

- **Package manager**: Poetry (`poetry install` to set up)
- **Lint**: `poetry run ruff check src/ tests/` and `poetry run ruff format --check src/ tests/`
- **Type check**: `poetry run mypy .`
- **Unit tests** (offline, mocked HTTP): `poetry run pytest tests/ --ignore=tests/custom/test_models_integration.py --ignore=tests/custom/test_coda_integration.py -v`
- **Integration tests** (needs API keys): `poetry run pytest tests/custom/test_models_integration.py tests/custom/test_coda_integration.py -v`
- **Full local CI**: `bash scripts/local_check_ci.sh` (add `--integration` for integration tests)

### Gotchas

- Poetry must be on `PATH`. If missing, run: `pip install poetry` and ensure `$HOME/.local/bin` is on `PATH`.
- `ruff check` currently has **9 pre-existing I001 (import sort) errors** in test files and Fern-generated test assets. These are known and not regressions.
- Integration tests require `CONDUCTOR_QUANTUM_API_KEY` env var. The Control API token and Coda API token (must start with `coda_`) are both derived from this key (see `tests/conftest.py`).
- The `tests/custom/test_client.py::test_client` test is `SKIPPED (Unimplemented)` — this is expected.
