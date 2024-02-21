from bot import bot, discord, commands
from utils.mongodb import ipdb


@bot.slash_command(
    name="infraction_points", description="Get the infraction points of a user"
)
@commands.guild_only()
async def infraction_points(
    interaction: discord.Interaction,
    user: discord.Member = discord.SlashOption(
        name="user", description="The user to get the infraction points of"
    ),
):
    user = ipdb.infraction_points.find_one(
        {"guild_id": interaction.guild.id, "user_id": user.id}
    )

    await interaction.send(
        f"{user.mention} has no infraction points"
        if user is None
        else f"{user.mention} has {user['points']} infraction points"
    )
