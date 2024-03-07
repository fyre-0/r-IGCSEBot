from bot import bot, discord, commands, traceback
from utils.constants import GUILD_ID, BOTLOG_CHANNEL_ID
from utils.mongodb import gpdb


@bot.event
async def on_command_error(ctx, exception):  # Deprecate soon??
    if isinstance(exception, commands.CommandNotFound):
        return
    description = f"Channel: {ctx.channel.mention}\nUser: {ctx.author.mention}\nGuild: {ctx.guild.name} ({ctx.guild.id})\n\nError:\n```{''.join(traceback.format_exception(exception, exception, exception.__traceback__))}```"
    embed = discord.Embed(title="An Exception Occured", description=description)
    botlogs = bot.get_channel(gpdb.get_pref("botlogs_channel", ctx.guild.id))
    if botlogs:
        await botlogs.send(embed=embed)
