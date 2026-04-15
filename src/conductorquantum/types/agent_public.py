import typing

import pydantic
from ..core.pydantic_utilities import IS_PYDANTIC_V2, UniversalBaseModel


class AgentPublic(UniversalBaseModel):
    """Public API model for Agent."""

    id: str = pydantic.Field()
    """The string ID of the agent."""

    name: str = pydantic.Field()
    """The name of the agent."""

    description: str = pydantic.Field()
    """The description of the agent."""

    if IS_PYDANTIC_V2:
        model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)  # type: ignore
    else:

        class Config:
            frozen = True
            smart_union = True
            extra = pydantic.Extra.allow
