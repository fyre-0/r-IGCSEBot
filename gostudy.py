from bot import discord, pymongo, traceback, time, tasks, commands, bot
from roles import has_role, is_moderator
from constants import TOKEN, LINK, GUILD_ID, FMROLE

@bot.slash_command(name="gostudy", description="disables the access to the offtopics for 1 hour.")
async def gostudy(interaction: discord.Interaction,
                  user: discord.User = discord.SlashOption(name="name", description="who do you want to use this command on?", required=False)):
        
      forced_mute_role = bot.get_guild(GUILD_ID).get_role(FMROLE)
      if user == None:
            user_id = interaction.user.id
            view = discord.ui.View(timeout=None)
            proceedBTN = discord.ui.Button(label="Proceed", style=discord.ButtonStyle.blurple)
            cancelBTN = discord.ui.Button(label="Cancel", style=discord.ButtonStyle.red)
            async def proceedCallBack(interaction):
                 unmute_tim = int(((time.time()) + 1) + 3600)
                 await message.delete()
                 dm = await interaction.user.create_dm()
                 await dm.send(f"Study time! You've been given a temporary break from the off-topic channels for the next hour, thanks to <@{interaction.user.id}>. Use this time to focus on your studies and make the most of it!\n\n Role will be removed <t:{unmute_tim}:R>")
                 await interaction.user.add_roles(forced_mute_role)
                 timern = int(time.time()) + 1
                 unmute_time = int(((time.time()) + 1) + 3600)
                 client = pymongo.MongoClient(LINK)
                 db = client.IGCSEBot
                 mute = db["mute"]
                 mute.insert_one({"_id": str(timern), "user_id": str(user_id),
                                  "unmute_time": str(unmute_time), "muted": True})
            proceedBTN.callback = proceedCallBack
            async def cancelCallBack(interaction):
                 await message.delete()
            cancelBTN.callback = cancelCallBack
            view.add_item(proceedBTN)
            view.add_item(cancelBTN)
            message = await interaction.send("Are we ready to move forward?", view=view, ephemeral=True)
      else:
            unmute_tim = int(((time.time()) + 1) + 3600)
            if not await is_moderator(interaction.user) and not await has_role(interaction.user, "Bot Developer"):
                  await interaction.send("You do not have the necessary permissions to perform this action", ephemeral = True)
                  return
            user_id = user.id
            user = bot.get_guild(GUILD_ID).get_member(user_id)
            view = discord.ui.View(timeout=None)
            proceedBTN = discord.ui.Button(label="Proceed", style=discord.ButtonStyle.blurple)
            cancelBTN = discord.ui.Button(label="Cancel", style=discord.ButtonStyle.red)
            async def proceedCallBack(interaction):
                 await message.delete()
                 dm = await user.create_dm()
                 await dm.send(f"Study time! You've been given a temporary break from the off-topic channels for the next hour, thanks to <@{interaction.user.id}>. Use this time to focus on your studies and make the most of it!\n\n Role will be removed <t:{unmute_tim}:R>")
                 await user.add_roles(forced_mute_role)
                 timern = int(time.time()) + 1
                 unmute_time = int(((time.time()) + 1) + 3600)
                 client = pymongo.MongoClient(LINK)
                 db = client.IGCSEBot
                 mute = db["mute"]
                 mute.insert_one({"_id": str(timern), "user_id": str(user_id),
                                  "unmute_time": str(unmute_time), "muted": True})
            proceedBTN.callback = proceedCallBack
            async def cancelCallBack(interaction):
                 await message.delete()
            cancelBTN.callback = cancelCallBack
            view.add_item(proceedBTN)
            view.add_item(cancelBTN)
            message = await interaction.send("Are we ready to move forward?", view=view, ephemeral=True)

@bot.slash_command(name="remove_gostudy", description="remove the Forced Mute role.")
async def remove_gostudy(interaction: discord.Interaction,
                  user: discord.User = discord.SlashOption(name="name", description="who do you want to use this command on?", required=False)):
        await interaction.response.defer(ephemeral = True)
        if not await is_moderator(interaction.user) and not await has_role(interaction.user, "Bot Developer"):
                  await interaction.send("You do not have the necessary permissions to perform this action", ephemeral = True)
                  return
        
        forced_mute_role = bot.get_guild(GUILD_ID).get_role(FMROLE)
        if user == None:
            user_id = interaction.user.id
            guild = bot.get_guild(GUILD_ID)
            member = guild.get_member(user_id)
            forced_mute_role = bot.get_guild(GUILD_ID).get_role(FMROLE)
            await member.remove_roles(forced_mute_role)
            client = pymongo.MongoClient(LINK)
            db = client.IGCSEBot
            mute = db["mute"]
            mute.delete_one({"user_id": str(user_id)})
            await interaction.send(f"the Forced mute role for <@{user_id}> has been removed", ephemeral=True)

        else:
            user_id = user.id
            user = bot.get_guild(GUILD_ID).get_member(user_id)
            guild = bot.get_guild(GUILD_ID)
            member = guild.get_member(user_id)
            forced_mute_role = bot.get_guild(GUILD_ID).get_role(FMROLE)
            await member.remove_roles(forced_mute_role)
            client = pymongo.MongoClient(LINK)
            db = client.IGCSEBot
            mute = db["mute"]
            mute.delete_one({"user_id": str(user_id)})
            await interaction.send(f"the Forced mute role for <@{user_id}> has been removed", ephemeral=True)
