from bot import bot, discord
from schemas.redis import EditedMessage


@bot.event
async def on_message_edit(before: discord.Message, after: discord.Message):
    if before.author.bot:
        return

    if before.content == after.content:
        return

    EditedMessage(
        channel_id=str(before.channel.id),
        content_before=before.content,
        content_after=after.content,
        author_name=before.author.name,
        author_icon_url=before.author.display_avatar.url,
        timestamp=str(after.edited_at.timestamp()),
    ).save().expire(90)
