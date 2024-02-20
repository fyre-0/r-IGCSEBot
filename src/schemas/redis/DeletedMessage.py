from redis_om import Field
from .ExtendedModel import ExtendedModel


class DeletedMessage(ExtendedModel):
    channel_id: str = Field(primary_key=True)
    content: str
    author_name: str
    author_icon_url: str
    timestamp: str
