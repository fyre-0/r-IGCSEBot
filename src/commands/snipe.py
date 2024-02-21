from bot import bot, discord, commands
from schemas.redis import DeletedMessage, EditedMessage
from redis_om import NotFoundError
import datetime


@bot.tree.command(name="snipe", description="Snipe a deleted/edited message")
@commands.guild_only()
async def snipe(
    interaction: discord.Interaction,
    type: str = discord.SlashOption(
        name="type",
        description="Edited or Deleted",
        default="Deleted",
        required=False,
        choices=["Deleted", "Edited"],
    ),
):
    if type == "Deleted":
        try:
            message = DeletedMessage.get(str(interaction.channel.id))
        except NotFoundError:
            await interaction.send("No deleted messages found", ephemeral=True)
            return

        embed = discord.Embed(
            title="Deleted Message",
            description=message.content,
            color=discord.Color.red(),
            timestamp=datetime.datetime.fromtimestamp(float(message.timestamp)),
        )

    elif type == "Edited":
        try:
            message = EditedMessage.get(str(interaction.channel.id))
        except NotFoundError:
            await interaction.send("No edited messages found", ephemeral=True)
            return

        embed = discord.Embed(
            title="Edited Message",
            description=f"**Before:** {message.content_before}\n**After:** {message.content_after}",
            color=discord.Color.yellow(),
            timestamp=datetime.datetime.fromtimestamp(float(message.timestamp)),
        )

    embed.set_author(
        name=message.author_name,
        icon_url=message.author_icon_url,
    )

    message.expire(0)

    await interaction.send(embed=embed)
