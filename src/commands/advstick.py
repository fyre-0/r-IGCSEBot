import time
from bot import discord, bot
from utils.constants import GUILD_ID
from utils.mongodb import smdb, gpdb


@bot.slash_command(
    name="advstick",
    description="sends a message in advance and automatically sticks it.")
async def advstick(
    interaction: discord.Interaction,
    channel: discord.TextChannel = discord.SlashOption(
        name="channel",
        description="Which channel do you want the message to be stuck on?",
        required=True,
    ),
    stick_time: str = discord.SlashOption(
        name="sticktime", description="Message Auto-Stick Time (Epoch)", required=True
    ),
    unstick_time: str = discord.SlashOption(
        name="unsticktime",
        description="Message Auto-Unstick Time (Epoch)",
        required=True,
    ),
    message_id: str = discord.SlashOption(
        name="messageid",
        description="ID of the message you want to stick in the future (must be in the current channel)",
        required=True,
    ),
):

    stick_time = int(stick_time)
    unstick_time = int(unstick_time)
    message_id = int(message_id)

    if stick_time < int(time.time()):
        await interaction.send(
            content="The stick time cannot be in the past.", ephemeral=True
        )
        return
    if unstick_time < stick_time:
        await interaction.send(
            content="The unstick time cannot be before the stick time.", ephemeral=True
        )
        return

    try:
        message = await channel.fetch_message(message_id)
    except discord.NotFound:
        await interaction.response.send_message("The requested message could not be found. It may have been deleted or the ID provided is incorrect.", ephemeral=True)
        return
    
    await smdb.timed_sticky(
        channel,
        message,
        stick_time,
        unstick_time,
    )

    timenow = int(time.time()) + 1

    mod_log_channel = bot.get_channel(gpdb.get_pref("modlog_channel", interaction.guild.id)) 
    if mod_log_channel:
        embed = discord.Embed(color=0xDEA6FF)
        embed.set_author(
            name=str(interaction.user), icon_url=interaction.user.display_avatar.url
        )
        embed.add_field(name="Scheduled Embed", value=f"[Jump to Embed/Message](https://discord.com/channels/{channel.guild.id}/{channel.id}/{message_id})", inline=False)
        embed.add_field(name="Stick time", value=f"<t:{stick_time}:R>", inline=False)
        embed.add_field(name="Unstick time", value=f"<t:{unstick_time}:R>", inline=False)
        embed.add_field(name="Date", value=f"<t:{timenow}:F>", inline=False)
        embed.add_field(
            name="ID",
            value=f"```py\nUser = {interaction.user.id}\nMessage = {message_id}```",
            inline=False,
        )
        embed.set_footer(text=f"{bot.user}", icon_url=bot.user.display_avatar.url)
        await mod_log_channel.send(embed=embed)
        
    await interaction.send(f"Advstick has been successfully scheduled to stick at <t:{stick_time}:F> (<t:{stick_time}:R>) and unstick at <t:{unstick_time}:F> (<t:{unstick_time}:R>)", ephemeral=True)