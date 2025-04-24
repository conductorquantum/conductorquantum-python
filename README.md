# ConductorQuantum Python Library

[![fern shield](https://img.shields.io/badge/%F0%9F%8C%BF-Built%20with%20Fern-brightgreen)](https://buildwithfern.com?utm_source=github&utm_medium=github&utm_campaign=readme&utm_source=https%3A%2F%2Fgithub.com%2Fconductorquantum%2Fconductorquantum-python)
[![pypi](https://img.shields.io/pypi/v/conductorquantum)](https://pypi.python.org/pypi/conductorquantum)

The ConductorQuantum Python library provides convenient access to the ConductorQuantum API from Python.

## Installation

```sh
pip install conductorquantum
```

## Reference

A full reference for this library is available [here](./reference.md).

## Usage

Instantiate and use the client with the following:

```python
from conductorquantum import ConductorQuantum

client = ConductorQuantum(
    token="YOUR_TOKEN",
)

# Using a file
with open("path/to/file.npy", "rb") as f:
    client.models.execute(
        model="coulomb-blockade-peak-detector-v1",
        data=f,
    )


# Using a numpy array
arr = np.array([2.643e-12, 2.164e-12 8.481e-13, ..., 2.320e-11, 2.153e-11, 1.984e-11])
client.models.execute(
    model="coulomb-blockade-peak-detector-v1",
    data=arr,
)
```

## Async Client

The SDK also exports an `async` client so that you can make non-blocking calls to our API.

```python
import asyncio

from conductorquantum import AsyncConductorQuantum

client = AsyncConductorQuantum(
    token="YOUR_TOKEN",
)


async def main() -> None:
    arr = np.array([2.643e-12, 2.164e-12 8.481e-13, ..., 2.320e-11, 2.153e-11, 1.984e-11])
    await client.models.execute(
        model="model",
        data=arr,
    )


asyncio.run(main())
```

## Exception Handling

When the API returns a non-success status code (4xx or 5xx response), a subclass of the following error
will be thrown.

```python
from conductorquantum.core.api_error import ApiError

try:
    client.models.execute(...)
except ApiError as e:
    print(e.status_code)
    print(e.body)
```

## Advanced

### Retries

The SDK is instrumented with automatic retries with exponential backoff. A request will be retried as long
as the request is deemed retriable and the number of retry attempts has not grown larger than the configured
retry limit (default: 2).

A request is deemed retriable when any of the following HTTP status codes is returned:

- [408](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/408) (Timeout)
- [429](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/429) (Too Many Requests)
- [5XX](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/500) (Internal Server Errors)

Use the `max_retries` request option to configure this behavior.

```python
client.models.execute(..., request_options={
    "max_retries": 1
})
```

### Timeouts

The SDK defaults to a 60 second timeout. You can configure this with a timeout option at the client or request level.

```python

from conductorquantum import ConductorQuantum

client = ConductorQuantum(
    ...,
    timeout=20.0,
)


# Override timeout for a specific method
client.models.execute(..., request_options={
    "timeout_in_seconds": 1
})
```

### Custom Client

You can override the `httpx` client to customize it for your use-case. Some common use-cases include support for proxies
and transports.
```python
import httpx
from conductorquantum import ConductorQuantum

client = ConductorQuantum(
    ...,
    httpx_client=httpx.Client(
        proxies="http://my.test.proxy.example.com",
        transport=httpx.HTTPTransport(local_address="0.0.0.0"),
    ),
)
```

## Contributing

While we value open-source contributions to this SDK, this library is generated programmatically.
Additions made directly to this library would have to be moved over to our generation code,
otherwise they would be overwritten upon the next generated release. Feel free to open a PR as
a proof of concept, but know that we will not be able to merge it as-is. We suggest opening
an issue first to discuss with us!

On the other hand, contributions to the README are always very welcome!
