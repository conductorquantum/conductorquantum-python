from __future__ import annotations

import os
import tempfile
import typing
from json.decoder import JSONDecodeError
from typing import Union, Any

import httpx
import numpy as np
import torch

from .base_client import BaseConductorQuantum, AsyncBaseConductorQuantum
from .core.api_error import ApiError
from .core.pydantic_utilities import parse_obj_as
from .core.request_options import RequestOptions
from .core import File
from .environment import ConductorQuantumEnvironment
from .errors.not_found_error import NotFoundError
from .errors.unprocessable_entity_error import UnprocessableEntityError
from .models.client import ModelsClient, AsyncModelsClient
from .types.http_validation_error import HttpValidationError
from .types.model_result_info import ModelResultInfo
from .types.models_enum import ModelsEnum

OMIT = typing.cast(Any, ...)

class UpdatedModelsClient(ModelsClient):
    def _convert_to_file(self, data: Union[File, np.ndarray, torch.Tensor]) -> File:
        """
        Convert input data to a File object if necessary.
        
        Parameters
        ----------
        data : Union[File, np.ndarray, torch.Tensor]
            The input data to convert
            
        Returns
        -------
        File
            A file object containing the data
        """
        if isinstance(data, (np.ndarray, torch.Tensor)):
            # Convert torch tensor to numpy if needed
            if isinstance(data, torch.Tensor):
                data = data.detach().cpu().numpy()
            
            # Create a temporary file and save the numpy array
            temp_file = tempfile.NamedTemporaryFile(suffix='.npy', delete=False)
            file_handle = None
            try:
                np.save(temp_file, data)
                temp_file.close()
                # Open in binary read mode for upload
                file_handle = open(temp_file.name, 'rb')
                return file_handle
            finally:
                # Schedule file for deletion after it's closed
                os.unlink(temp_file.name)
                if file_handle and file_handle.closed:
                    file_handle.close()
        return data

    def run(
        self, *, model: ModelsEnum, data: typing.Union[File, np.ndarray, torch.Tensor], request_options: typing.Optional[RequestOptions] = None
    ) -> ModelResultInfo:
        """
        Executes a model with the provided data.

        Parameters
        ----------
        model : ModelsEnum
            The model to run.

        data : Union[File, np.ndarray, torch.Tensor]
            The input data. Can be:
            - File: A file object (used as-is)
            - np.ndarray: A numpy array (automatically converted to .npy file)
            - torch.Tensor: A PyTorch tensor (converted to numpy then .npy file)

        request_options : typing.Optional[RequestOptions]
            Request-specific configuration.

        Returns
        -------
        ModelResultInfo
            Successful Response

        Raises
        ------
        NotFoundError
            If the model is not found.
        UnprocessableEntityError
            If the request is invalid.
        ApiError
            If there is an error processing the request.

        Examples
        --------
        from conductorquantum import ConductorQuantum
        import numpy as np
        import torch

        client = ConductorQuantum(
            token="YOUR_TOKEN",
        )

        # With a file
        client.models.execute(
            model="coulomb-blockade-peak-detector",
            data=my_file
        )

        # With a numpy array
        array_data = np.array([[1, 2], [3, 4]])
        client.models.execute(
            model="coulomb-blockade-peak-detector",
            data=array_data
        )

        # With a PyTorch tensor
        tensor_data = torch.tensor([[1, 2], [3, 4]])
        client.models.execute(
            model="coulomb-blockade-peak-detector",
            data=tensor_data
        )
        """
        file_obj = self._convert_to_file(data)
        _response = self._client_wrapper.httpx_client.request(
            "models",
            method="POST",
            data={
                "model": model,
            },
            files={
                "file": file_obj,
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


class ConductorQuantum(BaseConductorQuantum):
    def __init__(
        self,
        *,
        base_url: typing.Optional[str] = None,
        environment: ConductorQuantumEnvironment = ConductorQuantumEnvironment.DEFAULT,
        token: typing.Union[str, typing.Callable[[], str]],
        timeout: typing.Optional[float] = None,
        follow_redirects: typing.Optional[bool] = True,
        httpx_client: typing.Optional[httpx.Client] = None,
    ):
        super().__init__(
            base_url=base_url,
            environment=environment,
            token=token,
            timeout=timeout,
            follow_redirects=follow_redirects,
            httpx_client=httpx_client,
        )
        self.models = UpdatedModelsClient(client_wrapper=self._client_wrapper)


class AsyncUpdatedModelsClient(AsyncModelsClient):
    def _convert_to_file(self, data: Union[File, np.ndarray, torch.Tensor]) -> File:
        """
        Convert input data to a File object if necessary.
        
        Parameters
        ----------
        data : Union[File, np.ndarray, torch.Tensor]
            The input data to convert
            
        Returns
        -------
        File
            A file object containing the data
        """
        if isinstance(data, (np.ndarray, torch.Tensor)):
            # Convert torch tensor to numpy if needed
            if isinstance(data, torch.Tensor):
                data = data.detach().cpu().numpy()
            
            # Create a temporary file and save the numpy array
            temp_file = tempfile.NamedTemporaryFile(suffix='.npy', delete=False)
            file_handle = None
            try:
                np.save(temp_file, data)
                temp_file.close()
                # Open in binary read mode for upload
                file_handle = open(temp_file.name, 'rb')
                return file_handle
            finally:
                # Schedule file for deletion after it's closed
                os.unlink(temp_file.name)
                if file_handle and file_handle.closed:
                    file_handle.close()
        return data

    async def run(
        self, *, model: ModelsEnum, data: typing.Union[File, np.ndarray, torch.Tensor], request_options: typing.Optional[RequestOptions] = None
    ) -> ModelResultInfo:
        """
        Executes a model with the provided data.

        Parameters
        ----------
        model : ModelsEnum
            The model to run.

        data : Union[File, np.ndarray, torch.Tensor]
            The input data. Can be:
            - File: A file object (used as-is)
            - np.ndarray: A numpy array (automatically converted to .npy file)
            - torch.Tensor: A PyTorch tensor (converted to numpy then .npy file)

        request_options : typing.Optional[RequestOptions]
            Request-specific configuration.

        Returns
        -------
        ModelResultInfo
            Successful Response

        Raises
        ------
        NotFoundError
            If the model is not found.
        UnprocessableEntityError
            If the request is invalid.
        ApiError
            If there is an error processing the request.

        Examples
        --------
        from conductorquantum import AsyncConductorQuantum
        import numpy as np
        import torch
        import asyncio

        async def main():
            client = AsyncConductorQuantum(
                token="YOUR_TOKEN",
            )

            # With a file
            await client.models.execute(
                model="coulomb-blockade-peak-detector",
                data=my_file
            )

            # With a numpy array
            array_data = np.array([[1, 2], [3, 4]])
            await client.models.execute(
                model="coulomb-blockade-peak-detector",
                data=array_data
            )

            # With a PyTorch tensor
            tensor_data = torch.tensor([[1, 2], [3, 4]])
            await client.models.execute(
                model="coulomb-blockade-peak-detector",
                data=tensor_data
            )

        asyncio.run(main())
        """
        file_obj = self._convert_to_file(data)
        _response = await self._client_wrapper.httpx_client.request(
            "models",
            method="POST",
            data={
                "model": model,
            },
            files={
                "file": file_obj,
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


class AsyncConductorQuantum(AsyncBaseConductorQuantum):
    def __init__(
        self,
        *,
        base_url: typing.Optional[str] = None,
        environment: ConductorQuantumEnvironment = ConductorQuantumEnvironment.DEFAULT,
        token: typing.Union[str, typing.Callable[[], str]],
        timeout: typing.Optional[float] = None,
        follow_redirects: typing.Optional[bool] = True,
        httpx_client: typing.Optional[httpx.AsyncClient] = None,
    ):
        super().__init__(
            base_url=base_url,
            environment=environment,
            token=token,
            timeout=timeout,
            follow_redirects=follow_redirects,
            httpx_client=httpx_client,
        )
        self.models = AsyncUpdatedModelsClient(client_wrapper=self._client_wrapper)
