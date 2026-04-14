from conductorquantum.core import client_wrapper


def test_base_client_wrapper_uses_runtime_version(monkeypatch):
    monkeypatch.setattr(client_wrapper, "__version__", "9.8.7")

    wrapper = client_wrapper.BaseClientWrapper(
        token="test-token",
        base_url="https://example.com",
    )

    headers = wrapper.get_headers()

    assert headers["User-Agent"] == "conductorquantum/9.8.7"
    assert headers["X-Fern-SDK-Version"] == "9.8.7"
    assert headers["Authorization"] == "Bearer test-token"
