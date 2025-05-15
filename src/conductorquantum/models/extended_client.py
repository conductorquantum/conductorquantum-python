from __future__ import annotations

import os
import tempfile
import typing
from json.decoder import JSONDecodeError
from typing import Union, Any
import logging
import io

import numpy as np

from ..core.api_error import ApiError
from ..core.pydantic_utilities import parse_obj_as
from ..core.request_options import RequestOptions
from ..core import File
from ..errors.not_found_error import NotFoundError
from ..errors.unprocessable_entity_error import UnprocessableEntityError
from .client import ModelsClient, AsyncModelsClient
from ..types.http_validation_error import HttpValidationError
from ..types.model_result_public import ModelResultPublic

OMIT = typing.cast(Any, ...)

logger = logging.getLogger(__name__)


class ExtendedModelsClient(ModelsClient):
    """Extended models client that adds support for numpy arrays."""

    def _convert_to_file(
        self, data: Union[File, np.ndarray]
    ) -> tuple[File, typing.Optional[str]]:
        """
        Convert input data to a File object if necessary.

        Parameters
        ----------
        data : Union[File, np.ndarray]
            The input data to convert

        Returns
        -------
        tuple[File, Optional[str]]
            A file object containing the data and path to cleanup if temporary file was created
        """
        logger.info("Converting data to file in ExtendedModelsClient")
        if isinstance(data, np.ndarray):
            # Create a temporary file and save the numpy array
            temp_file = tempfile.NamedTemporaryFile(suffix=".npy", delete=False)
            temp_path = temp_file.name
            temp_file.close()  # Close immediately to avoid issues on Windows
            try:
                np.save(temp_path, data)
            except Exception as e:
                logger.error(f"Failed to save numpy array to file: {e}")
                try:
                    os.remove(
                        temp_path
                    )  # Use os.remove instead of unlink for better Windows compatibility
                except (OSError, PermissionError) as err:
                    logger.warning(
                        f"Failed to remove temporary file {temp_path}: {err}"
                    )
                raise
            # Open in binary read mode for upload
            file_handle = open(temp_path, "rb")
            return file_handle, temp_path
        return data, None

    def execute(
        self,
        *,
        model: str,
        data: typing.Union[File, np.ndarray],
        plot: typing.Optional[bool] = OMIT,
        dark_mode: typing.Optional[bool] = OMIT,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> ModelResultPublic:
        """Execute a model with the provided data."""
        logger.info(f"Executing model {model} in ExtendedModelsClient")
        file_obj, temp_path = self._convert_to_file(data)
        try:
            _response = self._raw_client._client_wrapper.httpx_client.request(  # pylint: disable=protected-access
                "models",
                method="POST",
                data={
                    "model": model,
                    "plot": plot,
                    "dark_mode": dark_mode,
                },
                files={
                    "data": file_obj,
                },
                request_options=request_options,
                omit=OMIT,
            )
            if 200 <= _response.status_code < 300:
                return typing.cast(
                    ModelResultPublic,
                    parse_obj_as(
                        type_=ModelResultPublic,  # type: ignore
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
        except JSONDecodeError as err:
            raise ApiError(
                status_code=_response.status_code, body=_response.text
            ) from err
        finally:
            # Clean up resources
            if isinstance(file_obj, (io.IOBase, typing.BinaryIO)):
                file_obj.close()
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(
                        temp_path
                    )  # Use os.remove instead of unlink for better Windows compatibility
                except (OSError, PermissionError) as err:
                    logger.warning(
                        f"Failed to remove temporary file {temp_path}: {err}"
                    )
        raise ApiError(status_code=_response.status_code, body=_response_json)


class AsyncExtendedModelsClient(AsyncModelsClient):
    """Async version of ExtendedModelsClient with support for numpy arrays."""

    def _convert_to_file(
        self, data: Union[File, np.ndarray]
    ) -> tuple[File, typing.Optional[str]]:
        """
        Convert input data to a File object if necessary.

        Parameters
        ----------
        data : Union[File, np.ndarray]
            The input data to convert

        Returns
        -------
        tuple[File, Optional[str]]
            A file object containing the data and path to cleanup if temporary file was created
        """
        logger.info("Converting data to file in ExtendedModelsClient")
        if isinstance(data, np.ndarray):
            # Create a temporary file and save the numpy array
            temp_file = tempfile.NamedTemporaryFile(suffix=".npy", delete=False)
            temp_path = temp_file.name
            temp_file.close()  # Close immediately to avoid issues on Windows
            try:
                np.save(temp_path, data)
            except Exception as e:
                logger.error(f"Failed to save numpy array to file: {e}")
                try:
                    os.remove(
                        temp_path
                    )  # Use os.remove instead of unlink for better Windows compatibility
                except (OSError, PermissionError) as err:
                    logger.warning(
                        f"Failed to remove temporary file {temp_path}: {err}"
                    )
                raise
            # Open in binary read mode for upload
            file_handle = open(temp_path, "rb")
            return file_handle, temp_path
        return data, None

    async def execute(
        self,
        *,
        model: str,
        data: typing.Union[File, np.ndarray],
        request_options: typing.Optional[RequestOptions] = None,
    ) -> ModelResultPublic:
        """
        Executes a model with the provided data.

        Parameters
        ----------
        model : str
            The model to run.

        data : Union[File, np.ndarray]
            The input data. Can be:
            - File: A file object (used as-is)
            - np.ndarray: A numpy array (automatically converted to .npy file)

        request_options : typing.Optional[RequestOptions]
            Request-specific configuration.

        Returns
        -------
        ModelResultPublic
            Successful Response

        Raises
        ------
        NotFoundError
            If the model is not found.
        UnprocessableEntityError
            If the request is invalid.
        ApiError
            If there is an error processing the request.
        """
        logger.info(f"Executing model {model} in ExtendedModelsClient")
        file_obj, temp_path = self._convert_to_file(data)
        try:
            _response = await self._raw_client._client_wrapper.httpx_client.request(  # pylint: disable=protected-access
                "models",
                method="POST",
                data={
                    "model": model,
                },
                files={
                    "data": file_obj,
                },
                request_options=request_options,
                omit=OMIT,
            )
            if 200 <= _response.status_code < 300:
                return typing.cast(
                    ModelResultPublic,
                    parse_obj_as(
                        type_=ModelResultPublic,  # type: ignore
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
        except JSONDecodeError as err:
            raise ApiError(
                status_code=_response.status_code, body=_response.text
            ) from err
        finally:
            # Clean up resources
            if isinstance(file_obj, (io.IOBase, typing.BinaryIO)):
                file_obj.close()
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(
                        temp_path
                    )  # Use os.remove instead of unlink for better Windows compatibility
                except (OSError, PermissionError) as err:
                    logger.warning(
                        f"Failed to remove temporary file {temp_path}: {err}"
                    )
        raise ApiError(status_code=_response.status_code, body=_response_json)
