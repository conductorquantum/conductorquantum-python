#!/usr/bin/env bash
#
# Run the same checks as CI locally.
#
# Usage:
#   ./local_check_ci.sh                     # lint + typecheck + unit tests
#   ./local_check_ci.sh --integration       # also run integration tests (needs CONDUCTOR_QUANTUM_API_KEY)
#
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
BOLD='\033[1m'
RESET='\033[0m'

pass() { echo -e "${GREEN}${BOLD}✓ $1${RESET}"; }
fail() { echo -e "${RED}${BOLD}✗ $1${RESET}"; exit 1; }
header() { echo -e "\n${BOLD}── $1 ──${RESET}"; }

RUN_INTEGRATION=false
for arg in "$@"; do
  case "$arg" in
    --integration) RUN_INTEGRATION=true ;;
  esac
done

# ---------------------------------------------------------------------------
# Lint
# ---------------------------------------------------------------------------
header "Ruff lint"
poetry run ruff check src/ tests/ && pass "ruff check" || fail "ruff check"

header "Ruff format check"
poetry run ruff format --check src/ tests/ && pass "ruff format" || fail "ruff format"

# ---------------------------------------------------------------------------
# Type check
# ---------------------------------------------------------------------------
header "Mypy"
poetry run mypy . && pass "mypy" || fail "mypy"

# ---------------------------------------------------------------------------
# Unit tests
# ---------------------------------------------------------------------------
header "Unit tests"
poetry run pytest tests/ \
  --ignore=tests/custom/test_models_integration.py \
  --ignore=tests/custom/test_coda_integration.py \
  -v && pass "unit tests" || fail "unit tests"

# ---------------------------------------------------------------------------
# Integration tests (optional)
# ---------------------------------------------------------------------------
if [ "$RUN_INTEGRATION" = true ]; then
  if [ -z "${CONDUCTOR_QUANTUM_API_KEY:-}" ]; then
    fail "CONDUCTOR_QUANTUM_API_KEY not set — required for integration tests"
  fi

  header "Integration tests (models)"
  poetry run pytest tests/custom/test_models_integration.py -v && pass "models integration" || fail "models integration"

  header "Integration tests (coda)"
  poetry run pytest tests/custom/test_coda_integration.py -v && pass "coda integration" || fail "coda integration"
fi

# ---------------------------------------------------------------------------
echo -e "\n${GREEN}${BOLD}All local CI checks passed.${RESET}"
