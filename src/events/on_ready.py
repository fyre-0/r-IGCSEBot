from bot import bot, discord
import pymongo
from utils.constants import (
    GUILD_ID,
    LINK,
    BETA,
    CHAT_MODERATOR_ROLE,
    guild_HELPER_ROLE,
    AL_HELPER_ROLE,
    BOT_DEVELOPER_ROLE,
    TEMP_MODERATOR_ROLE,
    STAFF_MODERATOR_ROLE,
)
from monitor_tasks import (
    checklock,
    checkmute,
    handle_slowmode,
    autorefreshhelpers,
    send_questions,
    expire_sessions,
    populate_cache,
    resetdmprefs,
)
from schemas.redis import View
from commands.practice.ui import MCQButtonsView
from utils.mongodb import smdb, gpdb

loops = [
    checklock,
    checkmute,
    autorefreshhelpers,
    handle_slowmode,
    send_questions,
    expire_sessions,
    populate_cache,
    resetdmprefs,
]


@bot.event
async def on_ready():
    print(f"Logged in as {str(bot.user)}.")
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.watching, name="r/IGCSE")
    ) 
    await smdb.populate_cache()
    for loop in loops:
        if loop and not loop.is_running():
            loop.start()
            
    views = View.find().all()
    for view in views:
        bot.add_view(
            MCQButtonsView(view["view_id"]), message_id=int(view["message_id"])
        )
    guilds = bot.guilds
    for guild in guilds:
        client = pymongo.MongoClient(LINK)
        db = client.IGCSEBot
        prefs = db["guild_preferences"]
        results = prefs.find({"guild_id": guild.id})
        for result in results:
            botlogid = result["botlogs_channel"]
            botlogs = bot.get_channel(botlogid)
            if botlogs:
                user = bot.user
                format = "%d-%m-%Y"
                embed = discord.Embed(
                    title=f"{bot.user.display_name} restarted successfully!", colour=0x51BB56
                )
                embed.add_field(
                    name="Bot Information",
                    value=f"```Name: {bot.user}\nCreated on: {bot.user.created_at.strftime(format)}\nJoined on: {guild.get_member(bot.user.id).joined_at.strftime(format)}\nBeta: {BETA}\nVerified: {user.verified}\nNo. of guilds: {len(bot.guilds)}\nID: {user.id}```",
                    inline=False,
                )
                embed.add_field(
                    name="Guild Information",
                    value=f"```Name: {guild.name}\nOwner: {guild.owner}\nCreated on: {guild.created_at.strftime(format)}\nMembers: {guild.member_count}\nBoosts: {guild.premium_subscription_count}\nID: {guild.id}```",
                    inline=False,
                )
                embed.add_field(
                    name="Channels & Commands",
                    value=f"```No. of roles: {len(guild.roles)}\nNo. of users: {len(guild.humans)}\nNo. of bots: {len(guild.bots)}\nNo. of catagories: {len(guild.categories)}\nNo. of text-channels: {len(guild.text_channels)}\nNo. of voice-channels: {len(guild.voice_channels)}\nNo. of forum-channels: {len(guild.forum_channels)}\nNo. of slash-commands: {len(bot.get_all_application_commands())}```",
                    inline=False,
                )
                embed.set_footer(text=f"{bot.user}", icon_url=bot.user.display_avatar.url)
                await botlogs.send(embed=embed)
