from bot import bot, discord
from schemas.redis import DeletedMessage


@bot.event
async def on_message_delete(message: discord.Message):
    if message.author.bot:
        return

    DeletedMessage(
        channel_id=str(message.channel.id),
        content=message.content,
        name=message.author.name,
        author_name=message.author.name,
        author_icon_url=message.author.display_avatar.url,
        timestamp=str(message.created_at.timestamp()),
    ).save().expire(90)
