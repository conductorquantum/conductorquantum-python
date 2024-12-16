# This file was auto-generated by Fern from our API Definition.

import typing
from ..core.client_wrapper import SyncClientWrapper
from ..types.models_enum import ModelsEnum
from ..core.request_options import RequestOptions
from ..types.model_info import ModelInfo
from ..core.jsonable_encoder import jsonable_encoder
from ..core.pydantic_utilities import parse_obj_as
from ..errors.not_found_error import NotFoundError
from ..errors.unprocessable_entity_error import UnprocessableEntityError
from ..types.http_validation_error import HttpValidationError
from json.decoder import JSONDecodeError
from ..core.api_error import ApiError
from .. import core
from ..types.model_result_info import ModelResultInfo
from ..core.client_wrapper import AsyncClientWrapper

# this is used as the default value for optional parameters
OMIT = typing.cast(typing.Any, ...)


class ModelsClient:
    def __init__(self, *, client_wrapper: SyncClientWrapper):
        self._client_wrapper = client_wrapper

    def info(self, model: ModelsEnum, *, request_options: typing.Optional[RequestOptions] = None) -> ModelInfo:
        """
        Retrieves a model's details.

        Parameters
        ----------
        model : ModelsEnum
            The model to get information for.

        request_options : typing.Optional[RequestOptions]
            Request-specific configuration.

        Returns
        -------
        ModelInfo
            Successful Response

        Examples
        --------
        from conductorquantum import ConductorQuantum

        client = ConductorQuantum(
            token="YOUR_TOKEN",
        )
        client.models.info(
            model="coulomb-blockade-peak-detector",
        )
        """
        _response = self._client_wrapper.httpx_client.request(
            f"models/{jsonable_encoder(model)}",
            method="GET",
            request_options=request_options,
        )
        try:
            if 200 <= _response.status_code < 300:
                return typing.cast(
                    ModelInfo,
                    parse_obj_as(
                        type_=ModelInfo,  # type: ignore
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

    def list(
        self,
        *,
        skip: typing.Optional[int] = None,
        limit: typing.Optional[int] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.List[ModelInfo]:
        """
        Retrieves a list of available models.

        Parameters
        ----------
        skip : typing.Optional[int]
            The number of models to skip.

        limit : typing.Optional[int]
            The number of models to include.

        request_options : typing.Optional[RequestOptions]
            Request-specific configuration.

        Returns
        -------
        typing.List[ModelInfo]
            Successful Response

        Examples
        --------
        from conductorquantum import ConductorQuantum

        client = ConductorQuantum(
            token="YOUR_TOKEN",
        )
        client.models.list()
        """
        _response = self._client_wrapper.httpx_client.request(
            "models",
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
                    typing.List[ModelInfo],
                    parse_obj_as(
                        type_=typing.List[ModelInfo],  # type: ignore
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

    def execute(
        self, *, model: ModelsEnum, data: core.File, request_options: typing.Optional[RequestOptions] = None
    ) -> ModelResultInfo:
        """
        Executes a model with the provided data.

        Parameters
        ----------
        model : ModelsEnum
            The model to run.

        data : core.File
            See core.File for more documentation

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
        client.models.execute(
            model="coulomb-blockade-peak-detector",
        )
        """
        _response = self._client_wrapper.httpx_client.request(
            "models",
            method="POST",
            data={
                "model": model,
            },
            files={
                "data": data,
            },
            request_options=request_options,
            omit=OMIT,
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


class AsyncModelsClient:
    def __init__(self, *, client_wrapper: AsyncClientWrapper):
        self._client_wrapper = client_wrapper

    async def info(self, model: ModelsEnum, *, request_options: typing.Optional[RequestOptions] = None) -> ModelInfo:
        """
        Retrieves a model's details.

        Parameters
        ----------
        model : ModelsEnum
            The model to get information for.

        request_options : typing.Optional[RequestOptions]
            Request-specific configuration.

        Returns
        -------
        ModelInfo
            Successful Response

        Examples
        --------
        import asyncio

        from conductorquantum import AsyncConductorQuantum

        client = AsyncConductorQuantum(
            token="YOUR_TOKEN",
        )


        async def main() -> None:
            await client.models.info(
                model="coulomb-blockade-peak-detector",
            )


        asyncio.run(main())
        """
        _response = await self._client_wrapper.httpx_client.request(
            f"models/{jsonable_encoder(model)}",
            method="GET",
            request_options=request_options,
        )
        try:
            if 200 <= _response.status_code < 300:
                return typing.cast(
                    ModelInfo,
                    parse_obj_as(
                        type_=ModelInfo,  # type: ignore
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

    async def list(
        self,
        *,
        skip: typing.Optional[int] = None,
        limit: typing.Optional[int] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.List[ModelInfo]:
        """
        Retrieves a list of available models.

        Parameters
        ----------
        skip : typing.Optional[int]
            The number of models to skip.

        limit : typing.Optional[int]
            The number of models to include.

        request_options : typing.Optional[RequestOptions]
            Request-specific configuration.

        Returns
        -------
        typing.List[ModelInfo]
            Successful Response

        Examples
        --------
        import asyncio

        from conductorquantum import AsyncConductorQuantum

        client = AsyncConductorQuantum(
            token="YOUR_TOKEN",
        )


        async def main() -> None:
            await client.models.list()


        asyncio.run(main())
        """
        _response = await self._client_wrapper.httpx_client.request(
            "models",
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
                    typing.List[ModelInfo],
                    parse_obj_as(
                        type_=typing.List[ModelInfo],  # type: ignore
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

    async def execute(
        self, *, model: ModelsEnum, data: core.File, request_options: typing.Optional[RequestOptions] = None
    ) -> ModelResultInfo:
        """
        Executes a model with the provided data.

        Parameters
        ----------
        model : ModelsEnum
            The model to run.

        data : core.File
            See core.File for more documentation

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
            await client.models.execute(
                model="coulomb-blockade-peak-detector",
            )


        asyncio.run(main())
        """
        _response = await self._client_wrapper.httpx_client.request(
            "models",
            method="POST",
            data={
                "model": model,
            },
            files={
                "data": data,
            },
            request_options=request_options,
            omit=OMIT,
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
