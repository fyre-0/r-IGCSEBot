from bot import bot, commands, discord, pymongo, tasks, time, traceback
from constants import FMROLE, GUILD_ID, LINK
from roles import has_role, is_moderator


@bot.slash_command(name="gostudy", description="Disables access to the offtopic channels for the next 1 hour.")
async def gostudy(
    interaction: discord.Interaction,
    user: discord.User = discord.SlashOption(
        name="name", description="Who do you want to use this command on? (only for Mods)", required=False
    ),
):
    guild = bot.get_guild(GUILD_ID)
    forced_mute_role = guild.get_role(FMROLE)

    user_id = interaction.user.id if user is None else user.id

    member = guild.get_member(user_id)

    view = discord.ui.View(timeout=None)
    proceedBTN = discord.ui.Button(label="Proceed", style=discord.ButtonStyle.blurple)
    cancelBTN = discord.ui.Button(label="Cancel", style=discord.ButtonStyle.red)

    async def proceedCallBack(interaction):
        unmute_time = int(((time.time()) + 1) + 3600)
        await message.delete()
        dm = await member.create_dm()
        await dm.send(
            f"Study time! You've been given a temporary break from the off-topic channels for the next hour. Use this time to focus on your studies and make the most of it!\n\n Role will be removed <t:{unmute_time}:R>"
        )
        await member.add_roles(forced_mute_role)
        timern = int(time.time()) + 1
        client = pymongo.MongoClient(LINK)
        db = client.IGCSEBot
        mute = db["mute"]
        mute.insert_one({"_id": str(timern), "user_id": str(user_id), "unmute_time": str(unmute_time), "muted": True})

    proceedBTN.callback = proceedCallBack

    async def cancelCallBack(interaction):
        await message.delete()

    cancelBTN.callback = cancelCallBack
    view.add_item(proceedBTN)
    view.add_item(cancelBTN)
    message = await interaction.send("Are we ready to move forward?", view=view, ephemeral=True)


@bot.slash_command(name="remove_gostudy", description="Remove the Study Mute role.")
async def remove_gostudy(
    interaction: discord.Interaction,
    user: discord.User = discord.SlashOption(
        name="name", description="Who do you want to use this command on?", required=False
    ),
):
    await interaction.response.defer(ephemeral=True)
    if not await is_moderator(interaction.user) and not await has_role(interaction.user, "Bot Developer"):
        await interaction.send("You do not have the necessary permissions to perform this action.", ephemeral=True)
        return

    guild = bot.get_guild(GUILD_ID)
    forced_mute_role = guild.get_role(FMROLE)

    user_id = user.id if user is not None else interaction.user.id

    member = guild.get_member(user_id)

    await member.remove_roles(forced_mute_role)
    client = pymongo.MongoClient(LINK)
    db = client.IGCSEBot
    mute = db["mute"]
    mute.delete_one({"user_id": str(user_id)})

    await interaction.send(f"The Study Mute role for <@{user_id}> has been removed.", ephemeral=True)
