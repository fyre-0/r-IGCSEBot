import time
import traceback
from constants import LINK, GUILD_ID
from bot import tasks, pymongo, discord, bot
from roles import get_role

async def togglechannellock(channelid, unlock, *, unlocktime=0):
    """Function for locking/unlocking a discord channel"""
    everyonerole = await get_role("@everyone")

    channel = bot.get_channel(channelid)
    overwrite = channel.overwrites_for(everyonerole)
    overwrite.send_messages = unlock

    await channel.set_permissions(everyonerole, overwrite=overwrite)
    await channel.send(f"{'Unl' if unlock else 'L'}ocked channel.")

    if not unlock:
      # If the channel was locked, send another embed with unlock time
      embed = discord.Embed(description=f"Unlocking channel <t:{unlocktime}:R>.")
      await channel.send(embed=embed)

@tasks.loop(seconds=6)
async def checklocks():
    """Checks the database every 60 seconds to see if anything needs to be locked or unlocked """
    client = pymongo.MongoClient(LINK)
    db = client.rigcse
    locks = db["channellock"]
    try:
        results = locks.find({"resolved": False})
        for result in results:
            if result["time"] <= time.time():
                # finds the unlock time
                ult = locks.find_one({"_id": "u" + result["_id"][1:]})["time"]
                await togglechannellock(result["channelid"], result["unlock"], unlocktime=ult)

                # Resolves the database entry (to avoid repeated locking/unlocking)
                locks.update_one({"_id": result["_id"]}, {"$set": {"resolved": True}})

    except Exception as e:
        print(traceback.format_exc())
        print(e)
