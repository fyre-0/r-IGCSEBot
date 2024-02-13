from bot import discord, bot


async def is_banned(user: discord.User | discord.Member, guild: discord.Guild):
    try:
        await guild.fetch_ban(user)
        return True
    except Exception:
        return False
