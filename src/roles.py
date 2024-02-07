from bot import discord, bot
from constants import GUILD_ID, MODERATOR_ROLES, CHAT_MODERATOR_ROLE, BOT_DEVELOPER_ROLE, TEMP_MODERATOR_ROLE

async def has_role(member: discord.Member, role_name: str):
    return any(role_name.lower() == role.lower() for role in member.roles)

async def get_role(role_name: str):
    return discord.utils.get(bot.get_guild(GUILD_ID).roles, name=role_name)

async def is_moderator(member: discord.Member):
    return any(role in [role.id for role in member.roles] for role in MODERATOR_ROLES) or member.guild_permissions.administrator

async def is_chat_moderator(member: discord.Member):
    return CHAT_MODERATOR_ROLE in [role.id for role in member.roles]

async def is_bot_developer(member: discord.Member):
    return BOT_DEVELOPER_ROLE in [role.id for role in member.roles]

async def is_server_booster(member: discord.Member):
    return await has_role(member, "Server Booster")

async def is_helper(member: discord.Member):
    return await has_role(member, "IGCSE Helper") or await has_role(member, 'AS/AL Helper')