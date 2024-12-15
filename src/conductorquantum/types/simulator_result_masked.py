# This file was auto-generated by Fern from our API Definition.

from ..core.pydantic_utilities import UniversalBaseModel
import pydantic
import datetime as dt
from ..core.pydantic_utilities import IS_PYDANTIC_V2
import typing


class SimulatorResultMasked(UniversalBaseModel):
    """
    Simulator result schema with the input data masked.
    """

    id: str = pydantic.Field()
    """
    The UUID of the simulator result.
    """

    simulator: str = pydantic.Field()
    """
    The id of the simulator used.
    """

    created_at: dt.datetime = pydantic.Field()
    """
    The UTC time the simulator result was created.
    """

    if IS_PYDANTIC_V2:
        model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)  # type: ignore # Pydantic v2
    else:

        class Config:
            frozen = True
            smart_union = True
            extra = pydantic.Extra.allow
