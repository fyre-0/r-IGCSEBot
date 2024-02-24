from bot import bot, discord
from schemas.redis import EditedMessage


@bot.event
async def on_message_edit(before: discord.Message, after: discord.Message):
    if (
        before.author.bot
        or before.guild is None
        or before.content == after.content
        or not before.channel.name == "counting"
    ):
        return

    await after.delete()
