from redis_om import Field
from .ExtendedModel import ExtendedModel


class EditedMessage(ExtendedModel):
    channel_id: str = Field(primary_key=True)
    content_before: str
    content_after: str
    author_name: str
    author_icon_url: str
    timestamp: str
