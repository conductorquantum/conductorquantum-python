from .base_client import \
  BaseConductorQuantum, AsyncBaseConductorQuantum

class ConductorQuantum(BaseConductorQuantum):
    """
    Use this class to access the different functions within the SDK. You can instantiate any number of clients with different configuration that will propagate to these functions.

    Parameters
    ----------
    base_url : typing.Optional[str]
        The base url to use for requests from the client.

    environment : ConductorQuantumEnvironment
        The environment to use for requests from the client. from .environment import ConductorQuantumEnvironment

        Defaults to ConductorQuantumEnvironment.DEFAULT

    token : typing.Union[str, typing.Callable[[], str]]
    timeout : typing.Optional[float]
        The timeout to be used, in seconds, for requests. By default the timeout is 60 seconds, unless a custom httpx client is used, in which case this default is not enforced.

    follow_redirects : typing.Optional[bool]
        Whether the default httpx client follows redirects or not, this is irrelevant if a custom httpx client is passed in.

    httpx_client : typing.Optional[httpx.Client]
        The httpx client to use for making requests, a preconfigured client is used by default, however this is useful should you want to pass in any custom httpx configuration.

    Examples
    --------
    from conductor_quantum import ConductorQuantum

    client = ConductorQuantum(
        token="YOUR_TOKEN",
    )
    """
    pass

class AsyncConductorQuantum(AsyncBaseConductorQuantum):
    """
    Use this class to access the different functions within the SDK. You can instantiate any number of clients with different configuration that will propagate to these functions.

    Parameters
    ----------
    base_url : typing.Optional[str]
        The base url to use for requests from the client.

    environment : ConductorQuantumEnvironment
        The environment to use for requests from the client. from .environment import ConductorQuantumEnvironment

        Defaults to ConductorQuantumEnvironment.DEFAULT

    token : typing.Union[str, typing.Callable[[], str]]
    timeout : typing.Optional[float]
        The timeout to be used, in seconds, for requests. By default the timeout is 60 seconds, unless a custom httpx client is used, in which case this default is not enforced.

    follow_redirects : typing.Optional[bool]
        Whether the default httpx client follows redirects or not, this is irrelevant if a custom httpx client is passed in.

    httpx_client : typing.Optional[httpx.AsyncClient]
        The httpx client to use for making requests, a preconfigured client is used by default, however this is useful should you want to pass in any custom httpx configuration.

    Examples
    --------
    from conductor_quantum import AsyncConductorQuantum

    client = AsyncConductorQuantum(
        token="YOUR_TOKEN",
    )
    """
    pass
