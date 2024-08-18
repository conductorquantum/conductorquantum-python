# This file was auto-generated by Fern from our API Definition.

from ..core.client_wrapper import SyncClientWrapper
import typing
from ..core.request_options import RequestOptions
from ..types.model_result_info import ModelResultInfo
from ..core.jsonable_encoder import jsonable_encoder
from ..core.pydantic_utilities import parse_obj_as
from ..errors.forbidden_error import ForbiddenError
from ..errors.not_found_error import NotFoundError
from ..errors.unprocessable_entity_error import UnprocessableEntityError
from ..types.http_validation_error import HttpValidationError
from json.decoder import JSONDecodeError
from ..core.api_error import ApiError
from ..types.model_result_masked import ModelResultMasked
from ..core.client_wrapper import AsyncClientWrapper


class ResultsClient:
    def __init__(self, *, client_wrapper: SyncClientWrapper):
        self._client_wrapper = client_wrapper

    def info(self, result_id: str, *, request_options: typing.Optional[RequestOptions] = None) -> ModelResultInfo:
        """
        Retrieves a model result.

        Parameters
        ----------
        result_id : str
            The UUID of the model result.

        request_options : typing.Optional[RequestOptions]
            Request-specific configuration.

        Returns
        -------
        ModelResultInfo
            Successful Response

        Examples
        --------
        from conductorquantum import ConductorQuantum

        client = ConductorQuantum(
            token="YOUR_TOKEN",
        )
        client.results.info(
            result_id="08047949-7263-4557-9122-ab293a49cae5",
        )
        """
        _response = self._client_wrapper.httpx_client.request(
            f"model-results/{jsonable_encoder(result_id)}",
            method="GET",
            request_options=request_options,
        )
        try:
            if 200 <= _response.status_code < 300:
                return typing.cast(
                    ModelResultInfo,
                    parse_obj_as(
                        type_=ModelResultInfo,  # type: ignore
                        object_=_response.json(),
                    ),
                )
            if _response.status_code == 403:
                raise ForbiddenError(
                    typing.cast(
                        typing.Optional[typing.Any],
                        parse_obj_as(
                            type_=typing.Optional[typing.Any],  # type: ignore
                            object_=_response.json(),
                        ),
                    )
                )
            if _response.status_code == 404:
                raise NotFoundError(
                    typing.cast(
                        typing.Optional[typing.Any],
                        parse_obj_as(
                            type_=typing.Optional[typing.Any],  # type: ignore
                            object_=_response.json(),
                        ),
                    )
                )
            if _response.status_code == 422:
                raise UnprocessableEntityError(
                    typing.cast(
                        HttpValidationError,
                        parse_obj_as(
                            type_=HttpValidationError,  # type: ignore
                            object_=_response.json(),
                        ),
                    )
                )
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    def delete(self, result_id: str, *, request_options: typing.Optional[RequestOptions] = None) -> None:
        """
        Deletes a model result.

        Parameters
        ----------
        result_id : str
            The UUID of the model result.

        request_options : typing.Optional[RequestOptions]
            Request-specific configuration.

        Returns
        -------
        None

        Examples
        --------
        from conductorquantum import ConductorQuantum

        client = ConductorQuantum(
            token="YOUR_TOKEN",
        )
        client.results.delete(
            result_id="08047949-7263-4557-9122-ab293a49cae5",
        )
        """
        _response = self._client_wrapper.httpx_client.request(
            f"model-results/{jsonable_encoder(result_id)}",
            method="DELETE",
            request_options=request_options,
        )
        try:
            if 200 <= _response.status_code < 300:
                return
            if _response.status_code == 403:
                raise ForbiddenError(
                    typing.cast(
                        typing.Optional[typing.Any],
                        parse_obj_as(
                            type_=typing.Optional[typing.Any],  # type: ignore
                            object_=_response.json(),
                        ),
                    )
                )
            if _response.status_code == 404:
                raise NotFoundError(
                    typing.cast(
                        typing.Optional[typing.Any],
                        parse_obj_as(
                            type_=typing.Optional[typing.Any],  # type: ignore
                            object_=_response.json(),
                        ),
                    )
                )
            if _response.status_code == 422:
                raise UnprocessableEntityError(
                    typing.cast(
                        HttpValidationError,
                        parse_obj_as(
                            type_=HttpValidationError,  # type: ignore
                            object_=_response.json(),
                        ),
                    )
                )
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    def list(
        self,
        *,
        skip: typing.Optional[int] = None,
        limit: typing.Optional[int] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.List[ModelResultMasked]:
        """
        Retrieves a list of model results.

        Parameters
        ----------
        skip : typing.Optional[int]
            The number of model results to skip.

        limit : typing.Optional[int]
            The number of model results to include.

        request_options : typing.Optional[RequestOptions]
            Request-specific configuration.

        Returns
        -------
        typing.List[ModelResultMasked]
            Successful Response

        Examples
        --------
        from conductorquantum import ConductorQuantum

        client = ConductorQuantum(
            token="YOUR_TOKEN",
        )
        client.results.list()
        """
        _response = self._client_wrapper.httpx_client.request(
            "model-results",
            method="GET",
            params={
                "skip": skip,
                "limit": limit,
            },
            request_options=request_options,
        )
        try:
            if 200 <= _response.status_code < 300:
                return typing.cast(
                    typing.List[ModelResultMasked],
                    parse_obj_as(
                        type_=typing.List[ModelResultMasked],  # type: ignore
                        object_=_response.json(),
                    ),
                )
            if _response.status_code == 404:
                raise NotFoundError(
                    typing.cast(
                        typing.Optional[typing.Any],
                        parse_obj_as(
                            type_=typing.Optional[typing.Any],  # type: ignore
                            object_=_response.json(),
                        ),
                    )
                )
            if _response.status_code == 422:
                raise UnprocessableEntityError(
                    typing.cast(
                        HttpValidationError,
                        parse_obj_as(
                            type_=HttpValidationError,  # type: ignore
                            object_=_response.json(),
                        ),
                    )
                )
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    def download(
        self, result_id: str, *, request_options: typing.Optional[RequestOptions] = None
    ) -> typing.Iterator[bytes]:
        """
        Downloads a model result as a JSON file zipped with the input file.

        Parameters
        ----------
        result_id : str
            The UUID of the model result.

        request_options : typing.Optional[RequestOptions]
            Request-specific configuration.

        Yields
        ------
        typing.Iterator[bytes]
            A zip file containing the model result as JSON and the input file.

        Examples
        --------
        from conductorquantum import ConductorQuantum

        client = ConductorQuantum(
            token="YOUR_TOKEN",
        )
        client.results.download(
            result_id="string",
        )
        """
        with self._client_wrapper.httpx_client.stream(
            f"model-results/{jsonable_encoder(result_id)}/download",
            method="GET",
            request_options=request_options,
        ) as _response:
            try:
                if 200 <= _response.status_code < 300:
                    for _chunk in _response.iter_bytes():
                        yield _chunk
                    return
                _response.read()
                if _response.status_code == 403:
                    raise ForbiddenError(
                        typing.cast(
                            typing.Optional[typing.Any],
                            parse_obj_as(
                                type_=typing.Optional[typing.Any],  # type: ignore
                                object_=_response.json(),
                            ),
                        )
                    )
                if _response.status_code == 404:
                    raise NotFoundError(
                        typing.cast(
                            typing.Optional[typing.Any],
                            parse_obj_as(
                                type_=typing.Optional[typing.Any],  # type: ignore
                                object_=_response.json(),
                            ),
                        )
                    )
                if _response.status_code == 422:
                    raise UnprocessableEntityError(
                        typing.cast(
                            HttpValidationError,
                            parse_obj_as(
                                type_=HttpValidationError,  # type: ignore
                                object_=_response.json(),
                            ),
                        )
                    )
                _response_json = _response.json()
            except JSONDecodeError:
                raise ApiError(status_code=_response.status_code, body=_response.text)
            raise ApiError(status_code=_response.status_code, body=_response_json)


class AsyncResultsClient:
    def __init__(self, *, client_wrapper: AsyncClientWrapper):
        self._client_wrapper = client_wrapper

    async def info(self, result_id: str, *, request_options: typing.Optional[RequestOptions] = None) -> ModelResultInfo:
        """
        Retrieves a model result.

        Parameters
        ----------
        result_id : str
            The UUID of the model result.

        request_options : typing.Optional[RequestOptions]
            Request-specific configuration.

        Returns
        -------
        ModelResultInfo
            Successful Response

        Examples
        --------
        import asyncio

        from conductorquantum import AsyncConductorQuantum

        client = AsyncConductorQuantum(
            token="YOUR_TOKEN",
        )


        async def main() -> None:
            await client.results.info(
                result_id="08047949-7263-4557-9122-ab293a49cae5",
            )


        asyncio.run(main())
        """
        _response = await self._client_wrapper.httpx_client.request(
            f"model-results/{jsonable_encoder(result_id)}",
            method="GET",
            request_options=request_options,
        )
        try:
            if 200 <= _response.status_code < 300:
                return typing.cast(
                    ModelResultInfo,
                    parse_obj_as(
                        type_=ModelResultInfo,  # type: ignore
                        object_=_response.json(),
                    ),
                )
            if _response.status_code == 403:
                raise ForbiddenError(
                    typing.cast(
                        typing.Optional[typing.Any],
                        parse_obj_as(
                            type_=typing.Optional[typing.Any],  # type: ignore
                            object_=_response.json(),
                        ),
                    )
                )
            if _response.status_code == 404:
                raise NotFoundError(
                    typing.cast(
                        typing.Optional[typing.Any],
                        parse_obj_as(
                            type_=typing.Optional[typing.Any],  # type: ignore
                            object_=_response.json(),
                        ),
                    )
                )
            if _response.status_code == 422:
                raise UnprocessableEntityError(
                    typing.cast(
                        HttpValidationError,
                        parse_obj_as(
                            type_=HttpValidationError,  # type: ignore
                            object_=_response.json(),
                        ),
                    )
                )
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    async def delete(self, result_id: str, *, request_options: typing.Optional[RequestOptions] = None) -> None:
        """
        Deletes a model result.

        Parameters
        ----------
        result_id : str
            The UUID of the model result.

        request_options : typing.Optional[RequestOptions]
            Request-specific configuration.

        Returns
        -------
        None

        Examples
        --------
        import asyncio

        from conductorquantum import AsyncConductorQuantum

        client = AsyncConductorQuantum(
            token="YOUR_TOKEN",
        )


        async def main() -> None:
            await client.results.delete(
                result_id="08047949-7263-4557-9122-ab293a49cae5",
            )


        asyncio.run(main())
        """
        _response = await self._client_wrapper.httpx_client.request(
            f"model-results/{jsonable_encoder(result_id)}",
            method="DELETE",
            request_options=request_options,
        )
        try:
            if 200 <= _response.status_code < 300:
                return
            if _response.status_code == 403:
                raise ForbiddenError(
                    typing.cast(
                        typing.Optional[typing.Any],
                        parse_obj_as(
                            type_=typing.Optional[typing.Any],  # type: ignore
                            object_=_response.json(),
                        ),
                    )
                )
            if _response.status_code == 404:
                raise NotFoundError(
                    typing.cast(
                        typing.Optional[typing.Any],
                        parse_obj_as(
                            type_=typing.Optional[typing.Any],  # type: ignore
                            object_=_response.json(),
                        ),
                    )
                )
            if _response.status_code == 422:
                raise UnprocessableEntityError(
                    typing.cast(
                        HttpValidationError,
                        parse_obj_as(
                            type_=HttpValidationError,  # type: ignore
                            object_=_response.json(),
                        ),
                    )
                )
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    async def list(
        self,
        *,
        skip: typing.Optional[int] = None,
        limit: typing.Optional[int] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.List[ModelResultMasked]:
        """
        Retrieves a list of model results.

        Parameters
        ----------
        skip : typing.Optional[int]
            The number of model results to skip.

        limit : typing.Optional[int]
            The number of model results to include.

        request_options : typing.Optional[RequestOptions]
            Request-specific configuration.

        Returns
        -------
        typing.List[ModelResultMasked]
            Successful Response

        Examples
        --------
        import asyncio

        from conductorquantum import AsyncConductorQuantum

        client = AsyncConductorQuantum(
            token="YOUR_TOKEN",
        )


        async def main() -> None:
            await client.results.list()


        asyncio.run(main())
        """
        _response = await self._client_wrapper.httpx_client.request(
            "model-results",
            method="GET",
            params={
                "skip": skip,
                "limit": limit,
            },
            request_options=request_options,
        )
        try:
            if 200 <= _response.status_code < 300:
                return typing.cast(
                    typing.List[ModelResultMasked],
                    parse_obj_as(
                        type_=typing.List[ModelResultMasked],  # type: ignore
                        object_=_response.json(),
                    ),
                )
            if _response.status_code == 404:
                raise NotFoundError(
                    typing.cast(
                        typing.Optional[typing.Any],
                        parse_obj_as(
                            type_=typing.Optional[typing.Any],  # type: ignore
                            object_=_response.json(),
                        ),
                    )
                )
            if _response.status_code == 422:
                raise UnprocessableEntityError(
                    typing.cast(
                        HttpValidationError,
                        parse_obj_as(
                            type_=HttpValidationError,  # type: ignore
                            object_=_response.json(),
                        ),
                    )
                )
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    async def download(
        self, result_id: str, *, request_options: typing.Optional[RequestOptions] = None
    ) -> typing.AsyncIterator[bytes]:
        """
        Downloads a model result as a JSON file zipped with the input file.

        Parameters
        ----------
        result_id : str
            The UUID of the model result.

        request_options : typing.Optional[RequestOptions]
            Request-specific configuration.

        Yields
        ------
        typing.AsyncIterator[bytes]
            A zip file containing the model result as JSON and the input file.

        Examples
        --------
        import asyncio

        from conductorquantum import AsyncConductorQuantum

        client = AsyncConductorQuantum(
            token="YOUR_TOKEN",
        )


        async def main() -> None:
            await client.results.download(
                result_id="string",
            )


        asyncio.run(main())
        """
        async with self._client_wrapper.httpx_client.stream(
            f"model-results/{jsonable_encoder(result_id)}/download",
            method="GET",
            request_options=request_options,
        ) as _response:
            try:
                if 200 <= _response.status_code < 300:
                    async for _chunk in _response.aiter_bytes():
                        yield _chunk
                    return
                await _response.aread()
                if _response.status_code == 403:
                    raise ForbiddenError(
                        typing.cast(
                            typing.Optional[typing.Any],
                            parse_obj_as(
                                type_=typing.Optional[typing.Any],  # type: ignore
                                object_=_response.json(),
                            ),
                        )
                    )
                if _response.status_code == 404:
                    raise NotFoundError(
                        typing.cast(
                            typing.Optional[typing.Any],
                            parse_obj_as(
                                type_=typing.Optional[typing.Any],  # type: ignore
                                object_=_response.json(),
                            ),
                        )
                    )
                if _response.status_code == 422:
                    raise UnprocessableEntityError(
                        typing.cast(
                            HttpValidationError,
                            parse_obj_as(
                                type_=HttpValidationError,  # type: ignore
                                object_=_response.json(),
                            ),
                        )
                    )
                _response_json = _response.json()
            except JSONDecodeError:
                raise ApiError(status_code=_response.status_code, body=_response.text)
            raise ApiError(status_code=_response.status_code, body=_response_json)
