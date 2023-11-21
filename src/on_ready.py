from constants import LINK, GUILD_ID, LOG_CHANNEL_ID
from bot import discord, bot
from checklocks import checklocks

@bot.event
async def on_ready():
    print(f"Logged in as {str(bot.user)}.")
    await bot.change_presence(activity=discord.Game(name="r/IGCSE"))
    embed = discord.Embed(title=f"Guilds Info ({len(bot.guilds)})", colour=0x3498db, description="Statistics about the servers this bot is in.")
    checklocks.start()

    for guild in bot.guilds:
        value = f"Owner: {guild.owner}\nMembers: {guild.member_count}\nBoosts: {guild.premium_subscription_count}"
        embed.add_field(name=guild.name, value=value, inline=True)
    igcse = await bot.fetch_guild(GUILD_ID)
    logs = await igcse.fetch_channel(LOG_CHANNEL_ID)
    await logs.send(embed=embed)
