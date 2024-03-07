from bot import bot, discord, traceback, pymongo
from utils.constants import GUILD_ID, LINK
from utils.mongodb import gpdb

@bot.event
async def on_application_command_error(interaction, exception):
    description = f"Channel: {interaction.channel.mention}\nUser: {interaction.user.mention}\nGuild: {interaction.guild.name} ({interaction.guild.id})\n\nError:\n```{''.join(traceback.format_exception(exception, exception, exception.__traceback__))}```"
    embed = discord.Embed(title="An Exception Occured", description=description)
    botlogs = bot.get_channel(gpdb.get_pref("botlogs_channel", interaction.guild.id)) 
    if botlogs:
        await botlogs.send(embed=embed)
