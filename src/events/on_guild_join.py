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
from utils.roles import is_moderator, is_helper, is_chat_moderator
import global_vars

@bot.event
async def on_guild_join(guild):
    chnl_name = 'bot-news'
    new_channel = await guild.create_text_channel(chnl_name)
    gpdb.set_pref("botnews_channel", new_channel.id, guild.id)