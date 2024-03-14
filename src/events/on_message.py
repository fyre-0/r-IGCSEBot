from utils.constants import (
    BETA,
    GUILD_ID,
    LINK,
)
from utils.data import REP_DISABLE_CHANNELS
from bot import discord, bot, keywords, datetime, time, pymongo
import sys
from commands.dms import send_dm
from utils.mongodb import gpdb, smdb, repdb, kwdb
from utils.roles import is_moderator, is_helper, is_chat_moderator, is_bot_developer
import global_vars

sticky_counter = {}
user_message_counts = {}
allowed_user_ids = {604335693757677588, 838682557976936509, 611165590744203285}

async def get_thread(message: discord.Message, is_dm: bool, guild_id):
      member_id: int = 0
      if is_dm: member_id = message.author.id
      else: member_id = int(message.content)

      guild = bot.get_guild(guild_id)
      member = guild.get_member(member_id)
      channel = guild.get_channel(gpdb.get_pref("dm_threads_channel", guild_id))
      if channel is not None:
        newmsg_channel = guild.get_channel(gpdb.get_pref("modmail_logs_channel", guild_id)) 
        threads = channel.threads
        thread_name = f"{member_id}"
        thread = discord.utils.get(threads, name=thread_name)
        if is_dm:
                if thread == None:
                    thread = await channel.create_thread(name=thread_name, content=f"Username: `{member.name}`\nUser ID: `{member_id}`")
                    embed = discord.Embed(title="New DM Recieved", description=f"Username: `{member.name}`\nUser ID: `{member_id}`\nThread: {thread.mention}", color=0xFF3E00)
                    await newmsg_channel.send(embed=embed)
                    return thread
                else:
                    embed = discord.Embed(title="New Message Recieved", description=f"Username: `{member.name}`\nUser ID: `{member_id}`\nThread: {thread.mention}", color=0x8DD5A2)
                    await newmsg_channel.send(embed=embed)
                    return thread       
        else:
                if thread == None:
                    thread = await channel.create_thread(name=thread_name, content=f"Username: `{member.name}`\nUser ID: `{member_id}`")
                    await message.reply(f"DM Channel has been created at {thread.mention}!")
                    return thread
                else:
                    await message.reply(f"DM Channel already exists for that user at {thread.mention}!")
                    return thread   


async def counting(message: discord.Message):
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
    except Exception:
        last_number = 0
        last_author = None

    try:
        if int(message.content) == last_number + 1 and last_author != message.author:
            await message.add_reaction("✅")
        else:
            await message.delete()
    except Exception:
        await message.delete()


async def is_welcome(text: str):
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


async def is_thanks(text: str):
    alternatives = [
        "thanks",
        "thank",
        "thank you",
        "thx",
        "tysm",
        "thank u",
        "thnks",
        "tanks",
        "thanku",
        "tyvm",
        "thankyou",
        "ty!",
    ]
    lowercase = text.lower()
    if "ty" in lowercase.split():
        return True
    else:
        for alternative in alternatives:
            if alternative in lowercase:
                return True


async def handle_rep(message: discord.Message):
    repped = []
    if message.reference:
        msg = await message.channel.fetch_message(message.reference.message_id)

    if (
        message.reference
        and msg.author != message.author
        and not msg.author.bot
        and not message.author.mentioned_in(msg)
        and (await is_welcome(message.content))
    ):
        repped = [message.author]
    elif await is_thanks(message.content):
        for mention in message.mentions:
            if mention == message.author:
                await message.channel.send(
                    f"Uh-oh, {message.author.mention}, you can't rep yourself!"
                )
            elif mention.bot:
                await message.channel.send(
                    f"Uh-oh, {message.author.mention}, you can't rep a bot!"
                )
            else:
                repped.append(mention)

    if repped and not BETA:
        for user in repped:
            rep = repdb.add_rep(user.id, message.guild.id)
            if rep == 100:
                role = discord.utils.get(user.guild.roles, name=f"{rep}+ Rep Club")
                await user.add_roles(role)
                await message.channel.send(
                    f"Gave +1 Rep to {user.mention} ({rep})\nWelcome to the {rep}+ Rep Club!"
                )
                hundredplusembed = discord.Embed(
                    title="Congratulations 100+ Reps!",
                    description=f"Congrats {user}! Thank you for your contribution towards our server. As our appreciation your dedication towards the server, we have added the ability for you to pick up your own color roles in ⁠<#946249349434863616>.\n\n**You may use the `/colorroles` command to do so. If you have any questions or need assistance, feel free to reply to this message.**",
                    color=0x8BF797,
                )              
                await send_dm(user, embed=hundredplusembed)
                channel = bot.get_channel(gpdb.get_pref("dm_threads_channel", message.guild.id)) 
                threads = channel.threads
                thread_name = f"{user.id}"
                thread = discord.utils.get(threads, name=thread_name)
                if thread is not None:
                    await thread.send(embed=hundredplusembed)
                else:
                    thread = await channel.create_thread(
                        name=thread_name,
                        content=f"Username: `{user.name}`\nUser ID: `{user.id}`",
                    )
                    await thread.send(embed=hundredplusembed)
            elif rep == 500:
                role = discord.utils.get(user.guild.roles, name=f"{rep}+ Rep Club")
                await user.add_roles(role)
                await message.channel.send(
                    f"Gave +1 Rep to {user.mention} ({rep})\nWelcome to the {rep}+ Rep Club!"
                )
            elif rep == 1000:
                role = discord.utils.get(user.guild.roles, name=f"{rep}+ Rep Club")
                await user.add_roles(role)
                await message.channel.send(
                    f"Gave +1 Rep to {user.mention} ({rep})\nWelcome to the {rep}+ Rep Club!"
                )
                thousandplusembed = discord.Embed(
                    title="Congratulations on 1000+ Reps!",
                    description=f"Congrats {user}! Thank you for your contribution towards our server. As our appreciation your dedication towards the server, we have added the additional colours to the colorrole command on the r/IGCSE Server! pick up your own color roles in ⁠<#946249349434863616>.\n\n**You may use the `/colorroles` command to do so. If you have any questions or need assistance, feel free to reply to this message.**",
                    color=0x8BF797,
                )                
                await send_dm(user, embed=thousandplusembed)
                channel = bot.get_channel(gpdb.get_pref("dm_threads_channel", message.guild.id)) 
                threads = channel.threads
                thread_name = f"{user.id}"
                thread = discord.utils.get(threads, name=thread_name)
                if thread is not None:
                    await thread.send(embed=thousandplusembed)
                else:
                    thread = await channel.create_thread(
                        name=thread_name,
                        content=f"Username: `{user.name}`\nUser ID: `{user.id}`",
                    )
                    await thread.send(embed=thousandplusembed)                
            else:
                await message.channel.send(f"Gave +1 Rep to {user} ({rep})")


@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    if message.type == discord.MessageType.premium_guild_subscription:
        user = message.author
        serverboosterembed = discord.Embed(
            title=f"Thank you for boosting {message.guild.name}",
            description=f"Thank you {message.author} for boosting our server! Your support means the world to us. As a token of our gratitude, we've enhanced the colorrole command on the r/IGCSE Server, offering more options for personalization. Pick up your own color roles in <#946249349434863616>.\n\n💡 Simply use the `/colorroles` command to get started. If you have any questions, feel free to reply to this message. We're here to help!",
            color=0x8BF797,
        )
        await send_dm(user, embed=serverboosterembed)
        channel = bot.get_channel(gpdb.get_pref("dm_threads_channel", message.guild.id)) 
        threads = channel.threads
        thread_name = f"{user.id}"
        thread = discord.utils.get(threads, name=thread_name)
        if thread is not None:
            await thread.send(embed=serverboosterembed)
        else:
            thread = await channel.create_thread(
                name=thread_name,
                content=f"Username: `{user.name}`\nUser ID: `{user.id}`",
            )
            await thread.send(embed=serverboosterembed)         


    if any(
        keyword in message.content.lower()
        for keyword in [
            "thanks",
            "thank",
            "thank you",
            "thx",
            "tysm",
            "thank u",
            "thnks",
            "tanks",
            "thanku",
            "tyvm",
            "thankyou",
            "ty!",
            "you're welcome",
            "your welcome",
            "ur welcome",
            "no problem",
            "np",
            "np!",
            "yw",
            "yw!",
        ]
    ):
        user_id = message.author.id
        current_time = datetime.datetime.utcnow()

        if user_id not in user_message_counts:
            user_message_counts[user_id] = {"count": 1, "timestamp": current_time}
        else:
            if current_time - user_message_counts[user_id][
                "timestamp"
            ] <= datetime.timedelta(minutes=3):
                user_message_counts[user_id]["count"] += 1
                if user_message_counts[user_id]["count"] > 8:
                    igcse = bot.get_guild(GUILD_ID)
                    channel = igcse.get_channel(1072835539998347307)
                    embed = discord.Embed(title="Potential Rep Farm", color=0xA10000)
                    embed.add_field(
                        name="Member", value=f"{message.author.mention}", inline=False
                    )
                    embed.add_field(
                        name="Channel", value=f"{message.channel.mention}", inline=False
                    )
                    embed.add_field(
                        name="Message Link",
                        value=f"[Jump to Message]({message.jump_url})",
                        inline=False,
                    )
                    embed.set_footer(
                        text=f"{bot.user}", icon_url=bot.user.display_avatar.url
                    )
                    await channel.send(embed=embed)
                    user_message_counts[user_id]["count"] = 0
            else:
                user_message_counts[user_id] = {"count": 1, "timestamp": current_time}

    if message.guild and bot.get_channel(gpdb.get_pref("create_dm_channel", message.guild.id)): 
        if message.channel == bot.get_channel(gpdb.get_pref("create_dm_channel", message.guild.id)): await get_thread(message, False, message.guild.id)

        if str(message.channel.type) in ["public_thread", "private_thread"] and message.channel.parent_id == gpdb.get_pref("dm_threads_channel", message.guild.id):
            member = message.guild.get_member(int(message.channel.name))
            if member == None:
                embed = discord.Embed(title="Error Encountered", description="I don't have permission to send direct messages to that user as they either left the server or has been banned/kicked.", colour=discord.Colour.red())
                embed.set_footer(text="DM Closed")
                await message.channel.send(embed=embed)
            channel = await member.create_dm()
            if message.stickers:
                for sticker in message.stickers:
                        sticker_name = sticker.name
                embed = discord.Embed(title="Message from r/IGCSE Moderators", description=f"{sticker_name} Sticker", colour=discord.Colour.green())
                embed.set_author(name=str(message.author), icon_url=message.author.display_avatar.url) 
            else:                  
                embed = discord.Embed(title="Message from r/IGCSE Moderators", description=message.clean_content, colour=discord.Colour.green())
                embed.set_author(name=str(message.author), icon_url=message.author.display_avatar.url)  
            try:
                for attachment in message.attachments:
                        if attachment.content_type == "image/png":
                            embed.set_image(url=attachment.url)
                        else:
                            embed.add_field(name=f"Attachments Added", value=f"{attachment.url}")
                await channel.send(embed=embed)
                await message.delete()
                await message.channel.send(embed=embed)
            except:
                perms = message.channel.overwrites_for(member)
                perms.send_messages, perms.read_messages, perms.view_channel, perms.read_message_history, perms.attach_files = True, True, True, True, True
                await message.channel.set_permissions(member, overwrite=perms)
                await message.channel.send(f"{member.mention}")
                return  

    if message.guild and message.guild.id == GUILD_ID:
        if message.channel.name == "bot-news":
            if not await is_moderator(message.author) and message.author.id not in allowed_user_ids: 
                return
            suffix = "\n\n~ r/IGCSE Bot Developer Team"
            messagecontent = message.clean_content + suffix
            guilds = bot.guilds
            for guild in guilds:
                bot_news = bot.get_channel(gpdb.get_pref("botnews_channel", guild.id))
                if bot_news is not None:
                    await bot_news.send(content=messagecontent)
                else:
                    new_channel = await guild.create_text_channel('bot-news')
                    gpdb.set_pref("botnews_channel", new_channel.id, guild.id)
                    time.sleep(1)
                    bot_news = bot.get_channel(gpdb.get_pref("botnews_channel", guild.id))
                    await bot_news.send(content=messagecontent)
                break
            await message.add_reaction("✅")

    if not message.guild:
        user = message.author
        timern = int(time.time()) + 1
        delete_time = int(time.time()) + 86400
        user_obj = bot.get_user(user.id)
        mutual_guilds = [guild for guild in user_obj.mutual_guilds]
        guild_ids = [guild.id for guild in mutual_guilds]
        no_mutual_guilds = len(mutual_guilds)
        msg = None    
        if message.content == ".swap":
            client = pymongo.MongoClient(LINK)
            db = client.IGCSEBot
            dmservers = db["dm_server_prefs"]
            pref = dmservers.delete_one({"user_id": user.id})  
            embed = discord.Embed(title="Select a server", description="Please select the server you want to send this message to. You can do so by reacting with the corresponding emote:\n\n", color=0xDDF19B)

            for i, guild in enumerate(mutual_guilds):
                emoji = f"{i+1}\N{COMBINING ENCLOSING KEYCAP}"
                embed.add_field(name=f"{emoji} {guild.name}", value=f"Guild ID: {guild.id}", inline=True)

            msg = await message.channel.send(embed=embed)

            for i in range(no_mutual_guilds):
                emoji = f"{i+1}\N{COMBINING ENCLOSING KEYCAP}"
                await msg.add_reaction(emoji)

            def check(reaction, user):
                return user == message.author and reaction.message.id == msg.id and str(reaction.emoji) in [f"{i+1}\N{COMBINING ENCLOSING KEYCAP}" for i in range(no_mutual_guilds)]

            reaction, _ = await bot.wait_for('reaction_add', check=check)
            selected_guild_id = guild_ids[int(reaction.emoji[0]) - 1]
            guild = bot.get_guild(selected_guild_id)
            dmservers.insert_one({"user_id": user.id, "chosen_guild": selected_guild_id, "created_time": timern, "deleted_time": delete_time, "resolved": False})
            await msg.delete()
            await message.channel.send(f"ModMail Server has been swapped to {guild.name}.")    
            return         

        if no_mutual_guilds != 1:
            client = pymongo.MongoClient(LINK)
            db = client.IGCSEBot
            dmservers = db["dm_server_prefs"]
            pref = dmservers.find_one({"user_id": user.id})

            if pref:
                selected_guild_id = pref["chosen_guild"]
            else:
                embed = discord.Embed(title="Select a server", description="Please select the server you want to send this message to. You can do so by reacting with the corresponding emote:\n\n", color=0xDDF19B)

                for i, guild in enumerate(mutual_guilds):
                    emoji = f"{i+1}\N{COMBINING ENCLOSING KEYCAP}"
                    embed.add_field(name=f"{emoji} {guild.name}", value=f"Guild ID: {guild.id}", inline=True)
                    embed.set_footer(text="use '.swap' to change Modmail Guilds/Servers")

                msg = await message.channel.send(embed=embed)

                for i in range(no_mutual_guilds):
                    emoji = f"{i+1}\N{COMBINING ENCLOSING KEYCAP}"
                    await msg.add_reaction(emoji)

                def check(reaction, user):
                    return user == message.author and reaction.message.id == msg.id and str(reaction.emoji) in [f"{i+1}\N{COMBINING ENCLOSING KEYCAP}" for i in range(no_mutual_guilds)]

                reaction, _ = await bot.wait_for('reaction_add', check=check)
                selected_guild_id = guild_ids[int(reaction.emoji[0]) - 1]
                dmservers.insert_one({"user_id": user.id, "chosen_guild": selected_guild_id, "created_time": timern, "deleted_time": delete_time, "resolved": False})
                await msg.delete()

            thread = await get_thread(message, True, selected_guild_id)
            sticker_name = None

            if message.stickers:
                for sticker in message.stickers:
                    sticker_name = sticker.name
                embed = discord.Embed(title="Message Received", description=f"{sticker_name} Sticker Received", colour=discord.Colour.green())
                embed.set_author(name=str(message.author), icon_url=message.author.display_avatar.url)
            else:
                embed = discord.Embed(title="Message Received", description=message.clean_content, colour=discord.Colour.green())
                embed.set_author(name=str(message.author), icon_url=message.author.display_avatar.url)

            for attachment in message.attachments:
                if attachment.content_type == "image/png":
                    embed.set_image(url=attachment.url)
                else:
                    embed.add_field(name=f"Attachments Added", value=f"{attachment.url}")

            await thread.send(embed=embed)
            await message.add_reaction("✅")
            return
        
        else:
            thread = await get_thread(message, True, guild_ids[0])
            sticker_name = None

            if message.stickers:
                for sticker in message.stickers:
                    sticker_name = sticker.name
                embed = discord.Embed(title="Message Received", description=f"{sticker_name} Sticker Received", colour=discord.Colour.green())
                embed.set_author(name=str(message.author), icon_url=message.author.display_avatar.url)
            else:
                embed = discord.Embed(title="Message Received", description=message.clean_content, colour=discord.Colour.green())
                embed.set_author(name=str(message.author), icon_url=message.author.display_avatar.url)

            for attachment in message.attachments:
                if attachment.content_type == "image/png":
                    embed.set_image(url=attachment.url)
                else:
                    embed.add_field(name=f"Attachments Added", value=f"{attachment.url}")

            await thread.send(embed=embed)
            await message.add_reaction("✅")
            return

    channel_id_rep = message.channel.id
    if isinstance(message.channel, discord.threads.Thread):
        # Threads have different IDs than parent channel
        channel_id_rep = message.channel.parent_id
    isrepchannel = channel_id_rep not in REP_DISABLE_CHANNELS
    if gpdb.get_pref("rep_enabled", message.guild.id) and isrepchannel:
        await handle_rep(message)
    if message.channel.name == "counting":
        await counting(message)

    if (
        message.guild.id == GUILD_ID
        and str(message.channel.id) in global_vars.sticky_channels
    ):
        sticky_counter[message.channel.id] = (
            sticky_counter.get(message.channel.id, 0) + 1
        )
        if sticky_counter[message.channel.id] >= 4:
            sticky_counter[message.channel.id] = 0
            await smdb.check_stick_msg(message)

    if message.content.lower() == "pin":
        if (
            await is_helper(message.author)
            or await is_moderator(message.author)
            or await is_chat_moderator(message.author)
            or await is_bot_developer(message.author)
        ):
            pins = await message.channel.pins()
            pin_no = len(pins)
            if pin_no == 50:
                await message.reply(
                    "Heads up! We've hit the pin limit for this channel. You can unpin some previously pinned messages to free up space."
                )
            msg = await message.channel.fetch_message(message.reference.message_id)
            await msg.pin()
            await msg.reply(
                f"This message has been pinned by {message.author.mention}."
            )
            await message.delete()

    if message.content.lower() == "unpin":
        if (
            await is_helper(message.author)
            or await is_moderator(message.author)
            or await is_chat_moderator(message.author)
            or await is_bot_developer(message.author)
        ):
            msg = await message.channel.fetch_message(message.reference.message_id)
            await msg.unpin()
            await msg.reply(
                f"This message has been unpinned by {message.author.mention}."
            )
            await message.delete()

    if message.content.lower() == "stick":
        if await is_moderator(message.author) or await is_bot_developer(message.author):
            if message.reference is not None:
                reference_msg = await message.channel.fetch_message(
                    message.reference.message_id
                )
                if await smdb.stick(reference_msg):
                    await message.reply(
                        f"Sticky message added by {message.author.mention}."
                    )

    if message.content.lower() == "unstick":
        if await is_moderator(message.author) or await is_bot_developer(message.author):
            if message.reference is not None:
                reference_msg = await message.channel.fetch_message(
                    message.reference.message_id
                )
                if await smdb.unstick(reference_msg):
                    await message.reply(
                        f"Sticky message removed by {message.author.mention}."
                    )

    if not keywords.get(message.guild.id, None):
        keywords[message.guild.id] = kwdb.get_keywords(message.guild.id)
    if message.content.lower() in keywords[message.guild.id].keys():
        autoreply = keywords[message.guild.id][message.content.lower()]
        if not autoreply.startswith("http"):  # If autoreply is a link/image/media
            keyword_embed = discord.Embed(
                description=autoreply, colour=discord.Colour.blue()
            )
            await message.channel.send(embed=keyword_embed)
        else:
            await message.channel.send(autoreply)

    await bot.process_commands(message)
