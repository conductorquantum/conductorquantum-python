"""Coda API exceptions."""

from __future__ import annotations

from typing import Any


class CodaAPIError(Exception):
    """Raised when the Coda API returns an error response."""

    def __init__(self, status_code: int, detail: str, body: dict[str, Any] | None = None) -> None:
        self.status_code = status_code
        self.detail = detail
        self.body = body
        super().__init__(f"[{status_code}] {detail}")


class CodaAuthError(CodaAPIError):
    """Raised on 401/403 authentication failures."""


class CodaTimeoutError(Exception):
    """Raised when a request times out."""
