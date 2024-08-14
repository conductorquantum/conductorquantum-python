# This file was auto-generated by Fern from our API Definition.

from ..core.pydantic_utilities import UniversalBaseModel
import datetime as dt
from ..core.pydantic_utilities import IS_PYDANTIC_V2
import typing
import pydantic


class ModelResult(UniversalBaseModel):
    output: str
    model_id: int
    input_file_gcs_path: str
    owner_id: int
    external_uuid: str
    created_at: dt.datetime
    id: int

    if IS_PYDANTIC_V2:
        model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)  # type: ignore # Pydantic v2
    else:

        class Config:
            frozen = True
            smart_union = True
            extra = pydantic.Extra.allow
