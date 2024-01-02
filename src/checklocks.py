import time
import traceback

from bot import bot, guild, pymongo, tasks
from constants import FMROLE, GUILD_ID, LINK


async def togglechannellock(channelid, unlock, *, unlocktime=0):
    # Function for locking/unlocking a discord channel
    everyone = bot.get_guild(GUILD_ID).default_role
    channel = bot.get_channel(channelid)
    overwrite = channel.overwrites_for(everyone)
    overwrite.send_messages_in_threads = unlock
    overwrite.send_messages = unlock

    try:
        await channel.set_permissions(everyone, overwrite=overwrite)
        await channel.send(f"Channel has been {'unl' if unlock else 'l'}ocked.")
        if not unlock:
            await channel.send(f"Unlocking channel <t:{unlocktime}:R>.")

    except Exception as e:
        print(traceback.format_exc())
        print(e)
        print("failed to set permissions")


async def toggleforumlock(threadid, unlock, unlocktime):
    thread = bot.get_channel(threadid)

    # Locking the post:
    try:
        thread = await thread.edit(locked=not unlock)
        await thread.send(f"Thread has been {'unl' if unlock else 'l'}ocked.")
        if not unlock:
            await thread.send(f"Unlocking channel <t:{unlocktime}:R>.")
    except Exception as e:
        print(traceback.format_exc())
        print(e)


@tasks.loop(seconds=60)
async def checklocks():
    # Checks the database every 60 seconds to see if anything needs to be locked or unlocked
    client = pymongo.MongoClient(LINK)
    db = client.IGCSEBot
    clocks = db["channellock"]
    flocks = db["forumlock"]

    try:
        results = clocks.find({"resolved": False})
        for result in results:
            if result["time"] <= time.time():
                # finds the unlock time
                ult = clocks.find_one({"_id": "u" + result["_id"][1:]})["time"]
                await togglechannellock(result["Channel_ID"], result["unlock"], unlocktime=ult)

                # Resolves the database entry (to avoid repeated locking/unlocking)
                clocks.update_one({"_id": result["_id"]}, {"$set": {"resolved": True}})

        results = flocks.find({"resolved": False})
        for result in results:
            if result["time"] <= time.time():
                # finds the unlock time
                ult = flocks.find_one({"_id": "u" + result["_id"][1:]})["time"]
                await toggleforumlock(result["Thread_ID"], result["unlock"], unlocktime=ult)
                # Resolves the database entry (to avoid repeated locking/unlocking)
                flocks.update_one({"_id": result["_id"]}, {"$set": {"resolved": True}})

    except Exception:
        print(traceback.format_exc())


@tasks.loop(seconds=25)
async def checktime():
    now = int(time.time())
    client = pymongo.MongoClient(LINK)
    db = client.IGCSEBot
    mute = db["mute"]
    for record in mute.find({"muted": True}):
        unmute_time = int(record["unmute_time"])
        if now >= unmute_time:
            member = guild.get_member(int(record["user_id"]))
            forced_mute_role = guild.get_role(FMROLE)
            if forced_mute_role in member.roles:
                await member.remove_roles(forced_mute_role)
                mute.update_one({"_id": record["_id"]}, {"$set": {"muted": False}})
                time.sleep(5)
                mute.delete_one({"_id": record["_id"]})
