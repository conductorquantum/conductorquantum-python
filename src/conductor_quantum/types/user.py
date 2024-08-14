# This file was auto-generated by Fern from our API Definition.

from ..core.pydantic_utilities import UniversalBaseModel
import pydantic
import datetime as dt
import typing
from .model_result import ModelResult
from ..core.pydantic_utilities import IS_PYDANTIC_V2


class User(UniversalBaseModel):
    auth0id: str = pydantic.Field(alias="auth0_id")
    created_at: dt.datetime
    id: int
    model_results: typing.Optional[typing.List[ModelResult]] = None

    if IS_PYDANTIC_V2:
        model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)  # type: ignore # Pydantic v2
    else:

        class Config:
            frozen = True
            smart_union = True
            extra = pydantic.Extra.allow
