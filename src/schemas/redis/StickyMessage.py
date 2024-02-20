from redis_om import Field
from .ExtendedModel import ExtendedModel


class StickyMessage(ExtendedModel):
    identifier: str = Field(primary_key=True)
    channel_id: str = Field(index=True)
    message_id: str = Field(index=True)
    content: list[dict[str, object]]
    enabled: int = Field(index=True)
