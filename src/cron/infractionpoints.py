import os
import nextcord as discord
from nextcord.ext import commands
import pymongo

intents = discord.Intents().all()
bot = commands.Bot(intents=intents)

TOKEN = os.environ.get("IGCSEBOT_TOKEN")
LINK = os.environ.get("MONGO_LINK")
GUILD_ID = 576460042774118420
ACTION_CHANNELID = 1209829023254057022

client = pymongo.MongoClient(
    LINK, server_api=pymongo.server_api.ServerApi("1"), minPoolSize=1
)
db = client.IGCSEBot
punishment_history = db.punishment_history


async def send_infraction_messages():
    guild = bot.get_guild(GUILD_ID)
    action_channel = guild.get_channel(ACTION_CHANNELID) or await guild.fetch_channel(
        ACTION_CHANNELID
    )
    points = punishment_history.aggregate(
        [
            {"$match": {"guild_id": "576460042774118420"}},
            {"$group": {"_id": "$action_against", "total_points": {"$sum": "$points"}}},
            {"$match": {"$expr": {"$gte": ["$total_points", 10]}}},
            {"$sort": {"total_points": -1}},
        ]
    )

    fields = []

    for point in points:
        try:
            user = guild.get_member(point["_id"]) or await guild.fetch_member(
                point["_id"]
            )
            if user is None:
                continue
            fields.append(
                {
                    "name": f"{user.name} ({user.id})",
                    "value": f"Total points: {point['total_points']}",
                }
            )
        except discord.errors.NotFound:
            continue
    
    if fields:
        embeds = []
        embed = discord.Embed(
            title="Infraction Points Leaderboard",
            description="The following users have accumulated 10 or more infraction points.",
            colour=0x1e293b,
        )
        
        for field in fields:
            if len(embed.fields) == 25:
                embeds.append(embed)
                embed = discord.Embed(
                    title=f"Infraction Points Leaderboard Page {len(embeds) + 1}",
                    description="The following users have accumulated 10 or more infraction points.",
                    colour=0x1e293b,
                )
            embed.add_field(name=field["name"], value=field["value"], inline=False)
            
        embeds.append(embed)
        
        await action_channel.send(embeds=embeds)
            

@bot.event
async def on_ready():
    print("Client ready, sending infraction messages")
    await send_infraction_messages()
    print("alright byee now")
    await bot.close()


bot.run(TOKEN)
