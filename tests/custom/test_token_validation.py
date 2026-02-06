import typing

import pytest

from conductorquantum.core.client_wrapper import BaseClientWrapper


def _build_wrapper(token: typing.Any) -> BaseClientWrapper:
    return BaseClientWrapper(
        token=token,
        base_url="https://api.example.com",
    )


def test_missing_token_raises_clear_error() -> None:
    wrapper = _build_wrapper(typing.cast(typing.Any, None))

    with pytest.raises(ValueError, match="Token is required but was not provided"):
        wrapper.get_headers()


def test_empty_token_raises_clear_error() -> None:
    wrapper = _build_wrapper("")

    with pytest.raises(ValueError, match="Token is required but was empty"):
        wrapper.get_headers()


def test_callable_returning_none_raises_clear_error() -> None:
    wrapper = _build_wrapper(lambda: typing.cast(typing.Any, None))

    with pytest.raises(ValueError, match="Token is required but was not provided"):
        wrapper.get_headers()


def test_non_string_token_raises_clear_error() -> None:
    wrapper = _build_wrapper(lambda: typing.cast(typing.Any, 123))

    with pytest.raises(ValueError, match="Token must be a string"):
        wrapper.get_headers()


def test_valid_token_sets_authorization_header() -> None:
    wrapper = _build_wrapper("abc123")

    headers = wrapper.get_headers()

    assert headers["Authorization"] == "Bearer abc123"
