from bot import bot, discord
from mongodb import dmsdb
from roles import is_chat_moderator, is_moderator
from constants import GUILD_ID, DMS_CLOSED_CHANNEL_ID

async def send_dm(member: discord.Member, **kwargs):
    try:
        await member.send(**kwargs)
    except:
        if member.guild.id == GUILD_ID:
            thread = await dmsdb.get_thread(member)
            await thread.send(**kwargs)
            await thread.send(content=member.mention)

@bot.slash_command(description="Deletes DM thread", guild_ids=[GUILD_ID], dm_permission=False)
async def delete_dm_thread(interaction: discord.Interaction, member: discord.Member = discord.SlashOption(name="member", description="Member to delete thread for (optional)", required=False)):
    if not member:
        if not await is_moderator(interaction.user) and not await is_chat_moderator(interaction.user):
            await interaction.send("You are not permitted to use this command.", ephemeral=True)
            return
    else:
        member = interaction.user # Guaranteed to be discord.Member
    
    thread = await dmsdb.get_thread(member, False)

    if not thread:
        await interaction.send("No thread found!", ephemeral=True)
    else:
        await dmsdb.del_thread(thread)
        await interaction.send("DM thread deleted! If DMs are still closed, a new thread will be made.", ephemeral=True)