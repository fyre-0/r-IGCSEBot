from constants import BETA, GUILD_ID, LOG_CHANNEL_ID, SHOULD_LOG_ALL, CREATE_DM_CHANNEL_ID
from bot import discord, bot, keywords
from db import gpdb, smdb, repdb, kwdb
from roles import is_moderator, is_helper

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
        members = [list(item.values())[0] for item in leaderboard[:3]]  # Creating list of Reputed member ids
        role = discord.utils.get(message.guild.roles, name="Reputed")
        if [member.id for member in role.members] != members:  # If Reputed has changed
            for m in role.members:
                await m.remove_roles(role)
            for member in members:
                member = message.guild.get_member(member)
                await member.add_roles(role)

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot: return

    igcse = await bot.fetch_guild(GUILD_ID)
    logs = await igcse.fetch_channel(LOG_CHANNEL_ID)

    if SHOULD_LOG_ALL:
        embed = discord.Embed(title="Message", description=message.content)
        embed.set_author(name=message.author.name, url=message.jump_url, icon_url=message.author.avatar.url)
        embed.add_field(name="Created", value=f"<t:{int(message.created_at.timestamp())}>")
        await logs.send(embed=embed)

    if not message.guild: # Modmail
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

    if message.channel.id == CREATE_DM_CHANNEL_ID:  # Creating modmail channels in #create-dm
        member = message.guild.get_member(int(message.content))
        category = discord.utils.get(message.guild.categories, name='COMMS')
        channel = discord.utils.get(category.channels, topic=str(member.id))
        if not channel:
            channel = await message.guild.create_text_channel(str(member).replace("#", "-"), category=category, topic=str(member.id))
        await message.reply(f"DM Channel has been created at {channel.mention}")

    if message.guild.id == GUILD_ID and message.channel.category:  # Sending modmails
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

    if gpdb.get_pref("rep_enabled", message.guild.id):
        await handle_rep(message)  # If message is replying to another message
    if message.channel.name == "counting":  # To facilitate #counting
        await counting(message)
    if message.guild.id == GUILD_ID:
        await smdb.check_stick_msg(message)

        if message.content.lower() == "pin":  # Pin a message
            if await is_helper(message.author) or await is_moderator(message.author):
                msg = await message.channel.fetch_message(message.reference.message_id)
                await msg.pin()
                await msg.reply(f"This message has been pinned by {message.author.mention}.")
                await message.delete()

        if message.content.lower() == "unpin":  # Unpin a message
            if await is_helper(message.author) or await is_moderator(message.author):
                msg = await message.channel.fetch_message(message.reference.message_id)
                await msg.unpin()
                await msg.reply(f"This message has been unpinned by {message.author.mention}.")
                await message.delete()
        
        if message.content.lower() == "stick": # Stick a message
            if await is_moderator(message.author):
                if message.reference is not None:
                        reference_msg = await message.channel.fetch_message(message.reference.message_id)
                        if await smdb.stick(reference_msg):
                            await message.reply(f"Sticky message added by {message.author.mention}.")

        if message.content.lower() == "unstick": # Unstick a message
            if await is_moderator(message.author):
                if message.reference is not None:
                    reference_msg = await message.channel.fetch_message(message.reference.message_id)
                    if await smdb.unstick(reference_msg):
                        await message.reply(f"Sticky message removed by {message.author.mention}.")

    if not keywords.get(message.guild.id, None):  # on first message from guild
        keywords[message.guild.id] = kwdb.get_keywords(message.guild.id)
    if message.content.lower() in keywords[message.guild.id].keys():
        autoreply = keywords[message.guild.id][message.content.lower()]
        if not autoreply.startswith("http"):  # If autoreply is a link/image/media
            keyword_embed = discord.Embed(description = autoreply, colour = discord.Colour.blue())
            await message.channel.send(embed = keyword_embed)
        else:
            await message.channel.send(autoreply)

    await bot.process_commands(message)
