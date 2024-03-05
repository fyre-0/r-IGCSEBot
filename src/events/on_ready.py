from bot import bot, discord
from utils.constants import (
    GUILD_ID,
    BOTLOG_CHANNEL_ID,
    BETA,
    CHAT_MODERATOR_ROLE,
    IGCSE_HELPER_ROLE,
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
)
from schemas.redis import View
from commands.practice.ui import MCQButtonsView
from utils.mongodb import smdb

loops = [
    checklock,
    checkmute,
    autorefreshhelpers,
    handle_slowmode,
    send_questions,
    expire_sessions,
    populate_cache,
]


@bot.event
async def on_ready():
    print(f"Logged in as {str(bot.user)}.")
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.watching, name="r/IGCSE")
    )
    guilds = bot.guilds
    for guild in guilds:
        if guild.name == "Palingenos's server" or guild.name == "jennifer's server" or guild.name == "school n study n shit" or guild.name == "Finals Study Group" or guild.name == "techno gamerz":
            await guild.leave
            print(f"Left {guild}")  
    await smdb.populate_cache()
    for loop in loops:
        if loop and not loop.is_running():
            loop.start()
            
    views = View.find().all()
    for view in views:
        bot.add_view(
            MCQButtonsView(view["view_id"]), message_id=int(view["message_id"])
        )
    igcse = bot.get_guild(GUILD_ID)
    botlogs = await igcse.fetch_channel(BOTLOG_CHANNEL_ID)
    user = bot.user
    format = "%d-%m-%Y"
    if not BETA:
        embed = discord.Embed(
            title=f"{bot.user.display_name} restarted successfully!", colour=0x51BB56
        )
        embed.add_field(
            name="Bot Information",
            value=f"```Name: {bot.user}\nCreated on: {bot.user.created_at.strftime(format)}\nJoined on: {igcse.get_member(bot.user.id).joined_at.strftime(format)}\nBeta: {BETA}\nVerified: {user.verified}\nNo. of guilds: {len(bot.guilds)}\nID: {user.id}```",
            inline=False,
        )
        embed.add_field(
            name="Guild Information",
            value=f"```Name: {igcse.name}\nOwner: {igcse.owner}\nCreated on: {igcse.created_at.strftime(format)}\nMembers: {igcse.member_count}\nBoosts: {igcse.premium_subscription_count}\nID: {igcse.id}```",
            inline=False,
        )
        embed.add_field(
            name="Role Statistics",
            value=f"```No. of roles: {len(igcse.roles)}\nIGCSE Helpers: {len(igcse.get_role(IGCSE_HELPER_ROLE).members)}\nAS/AL Helpers: {len(igcse.get_role(AL_HELPER_ROLE).members)}\nBot Developers: {len(igcse.get_role(BOT_DEVELOPER_ROLE).members)}\nStaff Moderators: {len(igcse.get_role(STAFF_MODERATOR_ROLE).members)}\nTemp Moderators: {len(igcse.get_role(TEMP_MODERATOR_ROLE).members)}\nChat Moderators: {len(igcse.get_role(CHAT_MODERATOR_ROLE).members)}```",
            inline=False,
        )
        embed.add_field(
            name="Channels & Commands",
            value=f"```No. of users: {len(igcse.humans)}\nNo. of bots: {len(igcse.bots)}\nNo. of catagories: {len(igcse.categories)}\nNo. of text-channels: {len(igcse.text_channels)}\nNo. of voice-channels: {len(igcse.voice_channels)}\nNo. of forum-channels: {len(igcse.forum_channels)}\nNo. of slash-commands: {len(bot.get_all_application_commands())}```",
            inline=False,
        )
        embed.set_footer(text=f"{bot.user}", icon_url=bot.user.display_avatar.url)
        await botlogs.send(embed=embed)
