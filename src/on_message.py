from constants import BETA, GUILD_ID, SHOULD_LOG_ALL, CREATE_DM_CHANNEL_ID, BOTLOG_CHANNEL_ID
from data import REP_DISABLE_CHANNELS, AUTO_SLOWMODE_CHANNELS, SUBJECT_CHANNELS, OFFTOPIC_CHANNELS
from bot import discord, bot, keywords, tasks
from mongodb import gpdb, smdb, repdb, kwdb
from roles import is_moderator, is_helper, is_chat_moderator, is_bot_developer
import threading
import time

channels_typing = {}
# for future reference: { "channel_id": [{ user_id, startedAt }, { user_id, startedAt }, { user_id, startedAt }] }

async def counting(message):
    if message.author.bot:
        await message.delete()
        return

    msgs = await message.channel.history(limit=2).flatten()
    try:
        msg = msgs[1]

        if "✅" in [str(reaction.emoji) for reaction in msg.reactions]:
            last_number = int(msg.content)
            last_author = msg.author
        else:
            last_number = 0
            last_author = None
    except:
        last_number = 0
        last_author = None

    try:
        if int(message.content) == last_number + 1 and last_author != message.author:
            await message.add_reaction("✅")
        else:
            await message.delete()
    except:
        await message.delete()
        
async def is_welcome(text):
    alternatives = ["you're welcome", "your welcome", "ur welcome", "no problem"]
    alternatives_2 = ["np", "np!", "yw", "yw!"]
    lowercase = text.lower()
    if "welcome" == lowercase:
        return True
    else:
        for alternative in alternatives:
            if alternative in lowercase:
                return True
        for alternative in alternatives_2:
            if alternative in lowercase.split() or alternative == lowercase:
                return True
    return False	  

async def is_thanks(text):
    alternatives = ["thanks", "thank you", "thx", "tysm", "thank u", "thnks", "tanks", "thankss" "thanku", "tyvm", "thankyou"]
    lowercase = text.lower()
    if "ty" in lowercase.split():
        return True
    else:
        for alternative in alternatives:
            if alternative in lowercase:
                return True
            
async def handle_rep(message):
      repped = []
      if message.reference:
            msg = await message.channel.fetch_message(message.reference.message_id)

      if message.reference and msg.author != message.author and not msg.author.bot and not message.author.mentioned_in(msg) and (await is_welcome(message.content)):
            repped = [message.author]
      elif await is_thanks(message.content):
            for mention in message.mentions:
                  if mention == message.author:
                        await message.channel.send(f"Uh-oh, {message.author.mention}, you can't rep yourself!")
                  elif mention.bot:
                        await message.channel.send(f"Uh-oh, {message.author.mention}, you can't rep a bot!")
                  else:
                        repped.append(mention)
                    
      if repped and not BETA:
            for user in repped:
                  rep = repdb.add_rep(user.id, message.guild.id)
                  if rep == 100 or rep == 500 or rep == 1000:
                        role = discord.utils.get(user.guild.roles, name=f"{rep}+ Rep Club")
                        await user.add_roles(role)
                        await message.channel.send(f"Gave +1 Rep to {user.mention} ({rep})\nWelcome to the {rep}+ Rep Club!")
                  else:
                        await message.channel.send(f"Gave +1 Rep to {user} ({rep})")
            leaderboard = repdb.rep_leaderboard(message.guild.id)
            members = [list(item.values())[0] for item in leaderboard[:3]]
            role = discord.utils.get(message.guild.roles, name="Reputed")
            if [member.id for member in role.members] != members:
                  for m in role.members:
                        await m.remove_roles(role)
                  for member in members:
                        member = message.guild.get_member(member)
                        await member.add_roles(role)

def typing_timer(channel_id, user_id, ttl):
    time.sleep(ttl)
    if channel_id not in channels_typing:
        return
    for x in channels_typing[channel_id]:
        if x["user_id"] == user_id:
            channels_typing[channel_id].remove(x)
            break

@bot.event
async def on_raw_typing(payload):
    if message.channel.id in AUTO_SLOWMODE_CHANNELS or message.channel.id in SUBJECT_CHANNELS or message.channel.id in OFFTOPIC_CHANNELS or not payload.guild_id:
        return
    if payload.channel_id not in channels_typing:
        channels_typing[payload.channel_id] = []
    if payload.user_id not in [x["user_id"] for x in channels_typing[payload.channel_id]]:
        channels_typing[payload.channel_id].append({"user_id": payload.user_id, "startedAt": payload.when})
    else:
        for x in channels_typing[payload.channel_id]:
            if x["user_id"] == payload.user_id:
                x["startedAt"] = payload.when

    # thread to automatically remove user from typing list after 10 seconds
    threading.Thread(target=typing_timer, args=(payload.channel_id, payload.user_id, 10)).start()

@tasks.loop(seconds=15)
async def handle_slowmode():
    global channels_typing
    for channel_id in channels_typing:
        channel = bot.get_channel(channel_id)
        if not channel:
            return
        number_of_users_typing = len(channels_typing[channel_id])
        slowmode = 0
            
        if number_of_users_typing >= 3:
            slowmode = 3
        elif number_of_users_typing >= 5:
            slowmode = 5
        elif number_of_users_typing >= 7:
            slowmode = 10
        elif number_of_users_typing >= 10:
            slowmode = 30
        elif number_of_users_typing >= 15:
            slowmode = 60
            
        if slowmode != channel.slowmode_delay:
           await channel.edit(slowmode_delay=slowmode)

handle_slowmode.start()

@bot.event
async def on_message(message: discord.Message):
      if message.author.bot: return
      igcse = await bot.fetch_guild(GUILD_ID)
      logs = await igcse.fetch_channel(BOTLOG_CHANNEL_ID)   

      if SHOULD_LOG_ALL:
            embed = discord.Embed(title="Message", description=message.content)
            embed.set_author(name=message.author.name, url=message.jump_url, icon_url=message.author.avatar.url)
            embed.add_field(name="Created", value=f"<t:{int(message.created_at.timestamp())}>")
            await logs.send(embed=embed) 

      if not message.guild:
            if message.content[0] == "/":
                  await message.reply("Uh-oh. We think you're trying to use a Slash Command. These can only be used within a Discord Server and not within DMs.")
            else:   
                  guild = bot.get_guild(GUILD_ID)
                  category = discord.utils.get(guild.categories, name='COMMS')
                  channel = discord.utils.get(category.channels, topic=str(message.author.id))
                  if not channel:
                        channel = await guild.create_text_channel(str(message.author).replace("#", "-"), category=category, topic=str(message.author.id))
                  embed = discord.Embed(title="Message Received", description=message.clean_content, colour=discord.Colour.green())
                  embed.set_author(name=str(message.author), icon_url=message.author.display_avatar.url)
                  await channel.send(embed=embed)
                  for attachment in message.attachments:
                        await channel.send(file=await attachment.to_file())
                  await message.add_reaction("✅")
                  return
            
      if message.channel.id == CREATE_DM_CHANNEL_ID:
            member = message.guild.get_member(int(message.content))
            category = discord.utils.get(message.guild.categories, name='COMMS')
            channel = discord.utils.get(category.channels, topic=str(member.id))
            if not channel:
                  channel = await message.guild.create_text_channel(str(member).replace("#", "-"), category=category, topic=str(member.id))
            await message.reply(f"DM Channel has been created at {channel.mention}")            

      if message.guild.id == GUILD_ID and message.channel.category:
            if message.channel.category.name.lower() == "comms" and not message.author.bot:
                  if int(message.channel.topic) == message.author.id:
                        return
                  else:
                        member = message.guild.get_member(int(message.channel.topic))
                        if message.content == ".sclose":
                              embed = discord.Embed(title="DM Channel Silently Closed", description=f"DM Channel with {member} has been closed by the moderators of r/IGCSE, without notifying the user.", colour=discord.Colour.green())
                              embed.set_author(name=str(message.author), icon_url=message.author.display_avatar.url)
                              await message.channel.delete()
                              await bot.get_channel(CREATE_DM_CHANNEL_ID).send(embed=embed)
                              return
                        channel = await member.create_dm()
                        if message.content == ".close":
                              embed = discord.Embed(title="DM Channel Closed", description=f"DM Channel with {member} has been closed by the moderators of r/IGCSE.", colour=discord.Colour.green())
                              embed.set_author(name=str(message.author), icon_url=message.author.display_avatar.url)
                              await channel.send(embed=embed)
                              await message.channel.delete()
                              await bot.get_channel(CREATE_DM_CHANNEL_ID).send(embed=embed)
                              return
                        embed = discord.Embed(title="Message from r/IGCSE Moderators", description=message.clean_content, colour=discord.Colour.green())
                        embed.set_author(name=str(message.author), icon_url=message.author.display_avatar.url)

                        try:
                              await channel.send(embed=embed)
                              for attachment in message.attachments:
                                    await channel.send(file=await attachment.to_file())
                              await message.channel.send(embed=embed)
                        except:
                              perms = message.channel.overwrites_for(member)
                              perms.send_messages, perms.read_messages, perms.view_channel, perms.read_message_history, perms.attach_files = True, True, True, True, True
                              await message.channel.set_permissions(member, overwrite=perms)
                              await message.channel.send(f"{member.mention}")
                              return

                        await message.delete()

      isrepchannel = not message.channel.id in REP_DISABLE_CHANNELS
      if gpdb.get_pref("rep_enabled", message.guild.id) and isrepchannel:
            await handle_rep(message)
      if message.channel.name == "counting":
            await counting(message)
      if message.guild.id == GUILD_ID:
            await smdb.check_stick_msg(message)

      if message.content.lower() == "pin":
            if await is_helper(message.author) or await is_moderator(message.author) or await is_chat_moderator(message.author):
                pins = await message.channel.pins()
                pin_no = len(pins)
                if pin_no == 50:
                    await message.reply(f"Heads up! We've hit the pin limit for this channel. You can unpin some previously pinned messages to free up space.")	
                msg = await message.channel.fetch_message(message.reference.message_id)
                await msg.pin()
                await msg.reply(f"This message has been pinned by {message.author.mention}.")
                await message.delete()

      if message.content.lower() == "unpin": 
            if await is_helper(message.author) or await is_moderator(message.author) or await is_chat_moderator(message.author):
                msg = await message.channel.fetch_message(message.reference.message_id)
                await msg.unpin()
                await msg.reply(f"This message has been unpinned by {message.author.mention}.")
                await message.delete()
        
      if message.content.lower() == "stick":
            if await is_moderator(message.author) or await is_bot_developer(message.author):
                if message.reference is not None:
                        reference_msg = await message.channel.fetch_message(message.reference.message_id)
                        if await smdb.stick(reference_msg):
                            await message.reply(f"Sticky message added by {message.author.mention}.")

      if message.content.lower() == "unstick":
            if await is_moderator(message.author) or await is_bot_developer(message.author):
                if message.reference is not None:
                    reference_msg = await message.channel.fetch_message(message.reference.message_id)
                    if await smdb.unstick(reference_msg):
                        await message.reply(f"Sticky message removed by {message.author.mention}.")            


      if not keywords.get(message.guild.id, None): 
            keywords[message.guild.id] = kwdb.get_keywords(message.guild.id)
      if message.content.lower() in keywords[message.guild.id].keys():
            autoreply = keywords[message.guild.id][message.content.lower()]
            if not autoreply.startswith("http"):  # If autoreply is a link/image/media
                  keyword_embed = discord.Embed(description = autoreply, colour = discord.Colour.blue())
                  await message.channel.send(embed = keyword_embed)
            else:
                  await message.channel.send(autoreply)

      if message.channel.id in AUTO_SLOWMODE_CHANNELS or message.channel.id in SUBJECT_CHANNELS or message.channel.id in OFFTOPIC_CHANNELS:
            for x in channels_typing[message.channel.id]:
                  if x["user_id"] == message.author.id:
                      channels_typing[message.channel.id].remove(x)
                      print(message.author.typing())
                      break

      await bot.process_commands(message)                        
                        
