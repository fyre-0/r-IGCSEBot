# Importing Variables
from bot import bot, datetime, discord, json, pymongo, requests, time, ast, traceback
from utils.constants import (
    GUILD_ID,
    LINK,
    TOKEN,
    FORCED_MUTE_ROLE,
)
from utils.data import (
    helper_roles,
    reactionroles_data,
    study_roles,
    subreddits,
    CIE_IGCSE_SUBJECT_CODES,
    CIE_ALEVEL_SUBJECT_CODES,
    CIE_OLEVEL_SUBJECT_CODES,
    ciealsubjectsdata,
    cieigsubjectsdata,
    cieolsubjectsdata,
    SESSION_ROLES,
    SUBJECT_ROLES,
    REP_DISABLE_CHANNELS,
)
from utils.roles import (
    is_moderator,
    is_server_booster,
    is_helper,
    get_role,
    has_role,
    is_chat_moderator,
    is_bot_developer,
)
from utils.mongodb import gpdb, repdb, rrdb, smdb, kwdb
import re

# Importing Files
from events import (
    on_ready,
    on_application_command_error,
    on_command_error,
    on_member_join,
    on_message,
    on_raw_reaction_add,
    on_raw_reaction_remove,
    on_thread_create,
    on_voice_state_update,
    auto_moderation,
    on_message_edit,
)
from commands import (
    role as role_command,
    colorroles,
    practice,
    locks as lock_command,
    chem_info,
    dms,
    gostudy,
    hotm,
    keywords,
    moderation,
    random_pyp,
    reputation,
    advstick,
)


def insert_returns(body):

    if isinstance(body[-1], ast.Expr):
        body[-1] = ast.Return(body[-1].value)
        ast.fix_missing_locations(body[-1])

    if isinstance(body[-1], ast.If):
        insert_returns(body[-1].body)
        insert_returns(body[-1].orelse)

    if isinstance(body[-1], ast.With):
        insert_returns(body[-1].body)


class EvalModal(discord.ui.Modal):
    def __init__(self):
        super().__init__("Execute a piece of code!", timeout=None)

        self.cmd = discord.ui.TextInput(
            label="Code",
            style=discord.TextInputStyle.paragraph,
            placeholder="Enter the code that is to be executed over here",
            required=True,
        )
        self.add_item(self.cmd)

    async def callback(self, interaction: discord.Interaction):
        fn_name = "_eval_expr"
        cmd = self.cmd.value.strip()
        cmd = "\n".join(f"    {i}" for i in cmd.splitlines())
        body = f"async def {fn_name}():\n{cmd}"
        parsed = ast.parse(body)
        body = parsed.body[0].body
        insert_returns(body)

        env = {
            "bot": bot,
            "discord": discord,
            "interaction": interaction,
            "__import__": __import__,
        }
        exec(compile(parsed, filename="<ast>", mode="exec"), env)

        result = await eval(f"{fn_name}()", env)
        await interaction.send(result)


@bot.slash_command(
    name="eval", description="Evaluate a piece of code.", guild_ids=[GUILD_ID]
)
async def _eval(interaction: discord.Interaction):
    if not await is_moderator(interaction.user):
        await interaction.send("This is not for you.", ephemeral=True)
        return
    eval_modal = EvalModal()
    await interaction.response.send_modal(eval_modal)


@bot.slash_command(
    name="rrmake", description="Create reaction roles", guild_ids=[GUILD_ID]
)
async def rrmake(
    interaction: discord.Interaction,
    link: str = discord.SlashOption(
        name="link",
        description="The link/id of the message to which the reaction roles will be added",
        required=True,
    ),
):
    if await is_moderator(interaction.user):
        guild = bot.get_guild(GUILD_ID)
        channel = interaction.channel
        try:
            msg_id = int(link.split("/")[-1])
            try:
                reaction_msg = await channel.fetch_message(msg_id)
            except discord.NotFound:
                await interaction.send("Invalid message", ephemeral=True)
            else:
                await interaction.send(
                    "Now, enter the reactions and their corresponding roles in the following format: `<Emoji> <@Role>`. Type 'stop' when you are done",
                    ephemeral=True,
                )
            rrs = []
            while True:
                rr_msg = await bot.wait_for(
                    "message",
                    check=lambda m: m.author == interaction.user
                    and m.channel == channel,
                )
                rr = str(rr_msg.content).lower()
                if rr == "stop":
                    break
                try:
                    reaction, role = rr.split()
                except ValueError:
                    await channel.send(
                        "You have to enter a reaction followed by a role separated by a space"
                    )
                else:
                    try:
                        int(role[3:-1])
                    except ValueError:
                        await interaction.send("Invalid Input", ephemeral=True)
                    else:
                        if guild.get_role(int(role[3:-1])) is None:
                            await interaction.send("Invalid Input", ephemeral=True)
                        else:
                            rrs.append([reaction, int(role[3:-1])])
                        await rr_msg.add_reaction("✅")
            for x in rrs:
                await reaction_msg.add_reaction(x[0])
                data = x.copy()
                data.append(msg_id)
                rrdb.new_rr(data)
            await interaction.send("Reaction Added!", ephemeral=True)
        except ValueError:
            await interaction.send("Invalid input", ephemeral=True)
    else:
        await interaction.send(
            "You do not have the necessary permissions to perform this action",
            ephemeral=True,
        )
        return


@bot.slash_command(description="Create a new in-channel poll")
async def yesnopoll(
    interaction: discord.Interaction,
    poll: str = discord.SlashOption(
        name="poll", description="The poll to be created", required=True
    ),
):
    embed = discord.Embed(
        title=poll,
        description=f"Total Votes: 0\n\n{'🟩' * 10}\n\n(from: {interaction.user})",
        colour=discord.Colour.purple(),
    )
    await interaction.send("Creating Poll.", ephemeral=True)
    msg1 = await interaction.channel.send(embed=embed)
    await msg1.add_reaction("✅")
    await msg1.add_reaction("❌")


class CancelPingBtn(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=890)
        self.value = True

    @discord.ui.button(label="Cancel Ping", style=discord.ButtonStyle.blurple)
    async def cancel_ping_btn(
        self, button: discord.ui.Button, interaction_b: discord.Interaction
    ):
        if (
            (interaction_b.user != self.user)
            and (not await is_helper(interaction_b.user))
            and (not await is_moderator(interaction_b.user))
        ):
            await interaction_b.send(
                "You do not have permission to do this.", ephemeral=True
            )
            return
        button.disabled = True
        self.value = False
        await self.message.edit(
            content=f"Ping cancelled by {interaction_b.user}", embed=None, view=None
        )

    async def on_timeout(self):
        await self.message.edit(view=None)
        if self.value:
            if self.message_id:
                url = f"https://discord.com/channels/{self.guild.id}/{self.channel.id}/{self.message_id}"
                embed = discord.Embed(description=f"[Jump to the message.]({url})")
            else:
                embed = discord.Embed()
            embed.set_author(name=str(self.user), icon_url=self.user.display_avatar.url)
            await self.message.channel.send(self.helper_role.mention, embed=embed)
            await self.message.delete()


@bot.slash_command(
    name="helper_old",
    description="[OUTDATED] pings helper for this subject in 15 minutes",
    guild_ids=[GUILD_ID],
)
async def helper_old(
    interaction: discord.Interaction,
):
    embed = discord.Embed(
        description="This command is now outdated, instead you can long-press/right-click on the message you want help with, go to 'Apps' then choose helper"
    )
    embed.set_image(
        url="https://raw.githubusercontent.com/fyre-0/r-IGCSEBot/assets/helper_ping.png"
    )

    await interaction.send(embed=embed, ephemeral=True)


@bot.message_command(
    name="helper",
    guild_ids=[GUILD_ID],
    default_member_permissions=discord.Permissions(
        send_messages=True, read_messages=True
    ),
)
async def helper(interaction: discord.Interaction, message: discord.Message):
    message_id = message.id
    try:
        helper_role = discord.utils.get(
            interaction.guild.roles, id=helper_roles[interaction.channel.id]
        )
    except Exception:
        await interaction.send(
            "There are no helper roles specified for this channel.", ephemeral=True
        )
        return
    roles = [role.name.lower() for role in interaction.user.roles]
    if "server booster" in roles:
        if message_id:
            url = f"https://discord.com/channels/{interaction.guild.id}/{interaction.channel.id}/{message_id}"
            embed = discord.Embed(description=f"[Jump to the message.]({url})")
            embed.set_author(
                name=str(interaction.user), icon_url=interaction.user.display_avatar.url
            )
        else:
            embed = discord.Embed()
            embed.set_author(
                name=str(interaction.user), icon_url=interaction.user.display_avatar.url
            )
        allowedMentions = discord.AllowedMentions()
        await interaction.send(
            content=helper_role.mention, embed=embed, allowed_mentions=allowedMentions
        )
        return
    view = CancelPingBtn()
    embed = discord.Embed(
        description=f"The helper role for this channel, `@{helper_role.name}`, will automatically be pinged (<t:{int(time.time() + 890)}:R>).\nIf your query has been resolved by then, please click on the `Cancel Ping` button."
    )
    embed.set_author(
        name=str(interaction.user), icon_url=interaction.user.display_avatar.url
    )
    message = await interaction.send(embed=embed, view=view)
    view.message = message
    view.channel = interaction.channel
    view.guild = interaction.guild
    view.message_id = message_id
    view.helper_role = helper_role
    view.user = interaction.user


@bot.command(
    name="refreshhelpers",
    description="Refresh the helper count in the description of subject channels",
    guild_ids=[GUILD_ID],
)
async def refreshhelpers(ctx):
    if not await is_moderator(ctx.author):
        return
    changed = []
    for chnl, role in helper_roles.items():
        try:
            helper_role = discord.utils.get(ctx.message.guild.roles, id=role)
            no_of_users = len(helper_role.members)
            channel = bot.get_channel(chnl)
            new_topic = None
            for line in channel.topic.split("\n"):
                if "No. of helpers" in line:
                    new_topic = channel.topic.replace(
                        line, f"No. of helpers: {no_of_users}"
                    )
                    break
            else:
                new_topic = f"{channel.topic}\nNo. of helpers: {no_of_users}"
            if channel.topic != new_topic:
                await channel.edit(topic=new_topic)
                changed.append(channel.mention)
        except Exception:
            continue
    if changed:
        mod_log_channel = bot.get_channel(gpdb.get_pref("modlog_channel", ctx.guild.id))
        timenow = int(time.time()) + 1
        embed = discord.Embed(description="Helpers Refreshed !!", color=0x51ADBB)
        embed.set_author(name=str(ctx.author), icon_url=ctx.author.display_avatar.url)
        embed.add_field(name="Channels", value=", ".join(changed), inline=False)
        embed.add_field(name="Date", value=f"<t:{timenow}:F>", inline=False)
        embed.add_field(
            name="ID",
            value=f"```py\nUser = {ctx.author.id}\nBot = {bot.user.id}```",
            inline=False,
        )
        embed.set_footer(text=f"{bot.user}", icon_url=bot.user.display_avatar.url)
        await mod_log_channel.send(embed=embed)
        await ctx.message.reply("Done! Changed channels: " + ", ".join(changed))
    else:
        await ctx.message.reply("No changes were made.")


@bot.command(description="Clear messages in a channel")
async def clear(ctx, num_to_clear: int):
    if not await is_moderator(ctx.author):
        return
    try:
        await ctx.channel.purge(limit=num_to_clear + 1)
    except Exception:
        await ctx.reply("Oops! I can only delete messages sent in the last 14 days")


@bot.slash_command(description="Pong!")
async def ping(interaction: discord.Interaction):
    await interaction.send("Pong!")


@bot.slash_command(name="joke", description="Get a random joke", guild_ids=[GUILD_ID])
async def joke(
    interaction: discord.Interaction,
    category: str = discord.SlashOption(
        name="category",
        description="Joke category",
        required=False,
        choices=["Programming", "Miscellaneous", "Dark", "Pun", "Spooky", "Christmas"],
    ),
):
    await interaction.response.defer()

    url = f"https://v2.jokeapi.dev/joke/{'Any' if category is None else category}?blacklistFlags=nsfw,religious,political,racist,sexist,explicit"
    res = requests.request("GET", url)

    if not res.ok:
        await interaction.send("Error fetching joke.")
        return

    data = json.loads(res.text)

    if data["type"] == "single":
        joke = data["joke"]
    else:
        joke = data["setup"] + "\n" + data["delivery"]

    await interaction.send(joke)


@bot.slash_command(name="meme", description="Get a random meme")
async def meme(
    interaction=discord.Interaction,
    subreddit: str = discord.SlashOption(
        name="subreddit", description="From which subreddit", required=False, default=""
    ),
):
    if subreddit != "" and re.match(r"^([a-z0-9][_a-z0-9]{2,20})$", subreddit) is None:
        await interaction.send("Invalid subreddit.")
        return

    await interaction.response.defer()

    async def get_sfw_meme():
        response = requests.request("GET", f"https://meme-api.com/gimme/{subreddit}")

        if not response.ok:
            await interaction.send("Error fetching meme.")
            return

        data = json.loads(response.text)

        if "count" in data:
            data = data["memes"][0]

        return data["url"] if not data["nsfw"] else get_sfw_meme()

    image_url = await get_sfw_meme()
    await interaction.send(image_url)


@bot.slash_command(
    name="search",
    description="Search for IGCSE past papers with subject code/question text",
)
async def search(
    interaction: discord.Interaction,
    query: str = discord.SlashOption(
        name="query", description="Search query", required=True
    ),
):
    await interaction.response.defer(ephemeral=True)
    try:
        response = requests.get(
            f"https://paper.sc/search/?as=json&query={query}"
        ).json()
        if len(response["list"]) == 0:
            await interaction.send(
                "No results found in past papers. Try changing your query for better results.",
                ephemeral=True,
            )
        else:
            embed = discord.Embed(
                title="Potential Match",
                description="Your question matched a past paper question!",
                colour=discord.Colour.green(),
            )
            for n, item in enumerate(response["list"][:3]):
                # embed.add_field(name="Result No.", value=str(n+1), inline=False)
                embed.add_field(
                    name="Subject", value=item["doc"]["subject"], inline=True
                )
                embed.add_field(name="Paper", value=item["doc"]["paper"], inline=True)
                embed.add_field(name="Session", value=item["doc"]["time"], inline=True)
                embed.add_field(
                    name="Variant", value=item["doc"]["variant"], inline=True
                )
                embed.add_field(
                    name="QP Link",
                    value=f"https://paper.sc/doc/{item['doc']['_id']}",
                    inline=True,
                )
                embed.add_field(
                    name="MS Link",
                    value=f"https://paper.sc/doc/{item['related'][0]['_id']}",
                    inline=True,
                )
            await interaction.send(embed=embed, ephemeral=True)
    except Exception:
        await interaction.send(
            "No results found in past papers. Try changing your query for better results.",
            ephemeral=True,
        )


@bot.slash_command(description="Set server preferences (for mods)")
async def set_preferences(
    interaction: discord.Interaction,
    modlog_channel: discord.abc.GuildChannel = discord.SlashOption(
        name="modlog_channel",
        description="Channel for log of timeouts, bans, etc.",
        required=False,
    ),
    rep_enabled: bool = discord.SlashOption(
        name="rep_enabled", description="Enable the reputation system?", required=False
    ),
    welcome_channel: discord.abc.GuildChannel = discord.SlashOption(
        name="welcome_channel",
        description="Channel for welcome messages.",
        required=False,
    ),
    warnlog_channel: discord.abc.GuildChannel = discord.SlashOption(
        name="warnlog_channel",
        description="Channel for warns to be logged.",
        required=False,
    ),
    behavior_log_channel: discord.abc.GuildChannel = discord.SlashOption(
        name="behavior_log_channel",
        description="Channel for logging user behavior.",
        required=False,
    ),
    feedback_channel: discord.abc.GuildChannel = discord.SlashOption(
        name="feedback_channel",
        description="Channel for receiving feedback from bot developers.",
        required=False,
    ),
    anon_confession_channel: discord.abc.GuildChannel = discord.SlashOption(
        name="anon_confession_channel",
        description="Channel for anonymous confessions.",
        required=False,
    ),
    counting_channel: discord.abc.GuildChannel = discord.SlashOption(
        name="counting_channel",
        description="Channel for counting.",
        required=False,
    ),
    chatmod_apps_channel: discord.abc.GuildChannel = discord.SlashOption(
        name="chatmod_apps_channel",
        description="Channel for chat moderation applications.",
        required=False,
    ),
    botlogs_channel: discord.abc.GuildChannel = discord.SlashOption(
        name="botlogs_channel",
        description="Channel for logs related to the bot's activities.",
        required=False,
    ),
    modmail_logs_channel: discord.abc.GuildChannel = discord.SlashOption(
        name="modmail_logs_channel",
        description="Channel for logging modmail interactions.",
        required=False,
    ),
    create_dm_channel: discord.abc.GuildChannel = discord.SlashOption(
        name="create_dm_channel",
        description="Channel for creating new DM threads.",
        required=False,
    ),
    closed_dm_channel: discord.abc.GuildChannel = discord.SlashOption(
        name="closed_dm_channel",
        description="Channel for closed DM threads.",
        required=False,
    ),
    dm_threads_channel: discord.abc.GuildChannel = discord.SlashOption(
        name="dm_threads_channel",
        description="Channel for ongoing DM threads.",
        required=False,
    ),
    confession_approval_channel: discord.abc.GuildChannel = discord.SlashOption(
        name="confession_approval_channel",
        description="Channel for approving anonymous confessions.",
        required=False,
    ),
    feedback_mods_channel: discord.abc.GuildChannel = discord.SlashOption(
        name="feedback_mods_channel",
        description="Channel for providing feedback to the mods.",
        required=False,
    ),
    hotm_results_channel: discord.abc.GuildChannel = discord.SlashOption(
        name="hotm_results_channel",
        description="Channel for displaying 'Hot of the Month' results.",
        required=False,
    ),
    study_session_channel: discord.abc.GuildChannel = discord.SlashOption(
        name="study_session_channel",
        description="Channel for coordinating study sessions.",
        required=False,
    ),
    action_required_channel: discord.abc.GuildChannel = discord.SlashOption(
        name="action_required_channel",
        description="Channel for notifying moderators about users who require action, such as bans.",
        required=False,
    ),
    botnews_channel: discord.abc.GuildChannel = discord.SlashOption(
        name="botnews_channel",
        description="Channel for bot-related news and updates.",
        required=False,
    ),
):

    if not await is_moderator(interaction.user):
        await interaction.send(
            "You are not authorized to perform this action", ephemeral=True
        )
        return

    if (
        not modlog_channel
        and not rep_enabled
        and not welcome_channel
        and not warnlog_channel
        and not behavior_log_channel
        and not feedback_channel
        and not anon_confession_channel
        and not counting_channel
        and not chatmod_apps_channel
        and not botlogs_channel
        and not modmail_logs_channel
        and not create_dm_channel
        and not closed_dm_channel
        and not dm_threads_channel
        and not confession_approval_channel
        and not feedback_mods_channel
        and not hotm_results_channel
        and not study_session_channel
        and not action_required_channel
        and not botnews_channel
    ):
        await interaction.send("Please input atleast one channel.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)
    guild_id = interaction.guild.id

    if modlog_channel:
        gpdb.set_pref("modlog_channel", modlog_channel.id, guild_id)
    if rep_enabled is not None:
        gpdb.set_pref("rep_enabled", rep_enabled, guild_id)
    if welcome_channel:
        gpdb.set_pref("welcome_channel", welcome_channel.id, guild_id)
    if warnlog_channel:
        gpdb.set_pref("warnlog_channel", warnlog_channel.id, guild_id)
    if behavior_log_channel:
        gpdb.set_pref("behavior_log_channel", behavior_log_channel.id, guild_id)
    if feedback_channel:
        gpdb.set_pref("feedback_channel", feedback_channel.id, guild_id)
    if anon_confession_channel:
        gpdb.set_pref("anon_confession_channel", anon_confession_channel.id, guild_id)
    if counting_channel:
        gpdb.set_pref("counting_channel", counting_channel.id, guild_id)
    if chatmod_apps_channel:
        gpdb.set_pref("chatmod_apps_channel", chatmod_apps_channel.id, guild_id)
    if botlogs_channel:
        gpdb.set_pref("botlogs_channel", botlogs_channel.id, guild_id)
    if modmail_logs_channel:
        gpdb.set_pref("modmail_logs_channel", modmail_logs_channel.id, guild_id)
    if create_dm_channel:
        gpdb.set_pref("create_dm_channel", create_dm_channel.id, guild_id)
    if closed_dm_channel:
        gpdb.set_pref("closed_dm_channel", closed_dm_channel.id, guild_id)
    if dm_threads_channel:
        gpdb.set_pref("dm_threads_channel", dm_threads_channel.id, guild_id)
    if feedback_mods_channel:
        gpdb.set_pref("feedback_mods_channel", feedback_mods_channel.id, guild_id)
    if confession_approval_channel:
        gpdb.set_pref(
            "confession_approval_channel", confession_approval_channel.id, guild_id
        )
    if hotm_results_channel:
        gpdb.set_pref("hotm_results_channel", hotm_results_channel.id, guild_id)
    if study_session_channel:
        gpdb.set_pref("study_session_channel", study_session_channel.id, guild_id)
    if action_required_channel:
        gpdb.set_pref("action_required_channel", action_required_channel.id, guild_id)
    if botnews_channel:
        gpdb.set_pref("botnews_channel", botnews_channel.id, guild_id)

    await interaction.send(
        "Guild preferences have been updated successfully!", ephemeral=True
    )


@bot.slash_command(description="Start a study session", guild_ids=[GUILD_ID])
async def study_session(interaction: discord.Interaction):
    try:
        role = interaction.guild.get_role(study_roles[interaction.channel.id])
    except Exception:
        await interaction.send(
            "Please use this command in the subject channel of the subject you're starting a study session for.",
            ephemeral=True,
        )
        return
    await interaction.response.defer()
    study_sesh_channel = bot.get_channel(
        gpdb.get_pref("study_session_channel", interaction.guild.id)
    )
    msg_history = await study_sesh_channel.history(limit=3).flatten()
    for msg in msg_history:
        if (
            str(interaction.user.mention) in msg.content
            or str(role.mention) in msg.content
        ) and (
            msg.created_at.replace(tzinfo=None) + datetime.timedelta(minutes=60)
            > datetime.datetime.utcnow()
        ):
            await interaction.send(
                "Please wait until one hour after your previous ping or after a study session in the same subject to start a new study session.",
                ephemeral=True,
            )
            return
    voice_channel = interaction.user.voice
    if voice_channel is None:
        await interaction.send(
            "You must be in a voice channel to use this command.", ephemeral=True
        )
    else:
        await study_sesh_channel.send(
            f"{role.mention} - Requested by {interaction.user.mention} - Please join {voice_channel.channel.mention}"
        )
        await interaction.send(
            f"Started a {role.name.lower().replace(' study ping', '').title()} study session at {voice_channel.channel.mention}."
        )
        await voice_channel.channel.edit(
            name=f"{role.name.lower().replace(' study ping', '').title()} Study Session"
        )


class Feedback(discord.ui.Modal):
    def __init__(self):
        super().__init__("Feedback!", timeout=None)

        self.feedback = discord.ui.TextInput(
            label="Your feedback",
            style=discord.TextInputStyle.paragraph,
            placeholder="The message you would like to send as feedback",
            required=True,
        )
        self.add_item(self.feedback)

    async def callback(self, interaction: discord.Interaction):
        feedback_channel = await bot.fetch_channel(FEEDBACK_CHANNEL_ID)
        feedback_embed = discord.Embed(
            title=f"{FEEDBACK_NAME} Received",
            description=self.feedback.value,
            colour=discord.Colour.blue(),
        )
        feedback_embed.set_author(
            name=str(interaction.user), icon_url=interaction.user.display_avatar.url
        )
        await feedback_channel.send(embed=feedback_embed)
        await interaction.send("Feedback sent!", ephemeral=True)


@bot.slash_command(name="feedback", description="Submit some feedback to the mods!")
async def feedback(
    interaction: discord.Interaction,
    target=discord.SlashOption(
        name="target",
        choices=["Moderators", "Bot Developers", "Resource Repository Team"],
        required=True,
    ),
):
    global FEEDBACK_CHANNEL_ID
    global FEEDBACK_NAME
    await interaction.response.send_modal(modal=Feedback())
    if target == "Bot Developers":
        FEEDBACK_CHANNEL_ID = gpdb.get_pref("feedback_channel", interaction.guild.id)
        FEEDBACK_NAME = "Bot Feedback"
    elif target == "Moderators":
        FEEDBACK_CHANNEL_ID = gpdb.get_pref(
            "feedback_mods_channel", interaction.guild.id
        )
        FEEDBACK_NAME = "Mod Feedback"
    else:
        FEEDBACK_CHANNEL_ID = gpdb.get_pref(
            "feedback_mods_channel", interaction.guild.id
        )
        FEEDBACK_NAME = "Repository Feedback"


@bot.command(name="sync_commands")
async def sync_commands(ctx: discord.Message):
    if not await is_moderator(ctx.author) and not await is_bot_developer(ctx.author):
        return
    bot.add_all_application_commands()
    await bot.sync_application_commands()
    await ctx.message.reply("Slash commands syncronized.")


@bot.slash_command(description="Get a random fun fact")
async def funfact(interaction: discord.Interaction):
    await interaction.response.defer()
    url = "https://uselessfacts.jsph.pl/random.json?language=en"
    response = requests.request("GET", url)
    data = json.loads(response.text)
    useless_fact = data["text"]
    await interaction.send(useless_fact)


@bot.slash_command(
    name="instant_lockdown",
    description="Instantly locks/unlocks a channel/thread (for mods)",
)
async def Instantlockcommand(
    interaction: discord.Interaction,
    action_type: str = discord.SlashOption(
        name="action_type",
        description="FORUM THREAD OR CHANNEL?",
        choices=["Channel Lock", "Forum Lock"],
        required=True,
    ),
    channelinput: discord.TextChannel = discord.SlashOption(
        name="channel_name",
        description="Which channel do you want to perform the action on? (for channel lock)",
        required=False,
    ),
    threadinput: discord.Thread = discord.SlashOption(
        name="thread_name",
        description="Which thread do you want to perform the action on? (for forum lock)",
        required=False,
    ),
):
    await interaction.response.defer(ephemeral=True)
    if not await is_moderator(interaction.user):
        await interaction.send(
            f"Sorry {interaction.user.mention},"
            " you don't have the permission to perform this action.",
            ephemeral=True,
        )
        return
    mod_log_channel = bot.get_channel(
        gpdb.get_pref("modlog_channel", interaction.guild.id)
    )
    if mod_log_channel:
        timenow = int(time.time()) + 1
        if action_type == "Forum Lock":
            if threadinput is None:
                await interaction.send(
                    "Please mention the forum post in the `thread_name` field.",
                    ephemeral=True,
                )
            else:
                thread_id = bot.get_channel(threadinput.id)
                if not thread_id.locked:
                    thread = await thread_id.edit(locked=True)
                    embed = discord.Embed(
                        description="Instant Forum Lockdown",
                        colour=discord.Colour.red(),
                    )
                    embed.set_author(
                        name=str(interaction.user),
                        icon_url=interaction.user.display_avatar.url,
                    )
                    embed.add_field(
                        name="Locked Thread", value=f"<#{threadinput.id}>", inline=False
                    )
                    embed.add_field(name="Date", value=f"<t:{timenow}:F>", inline=False)
                    embed.add_field(
                        name="ID",
                        value=f"```py\nUser = {interaction.user.id}\nThread = {threadinput.id}```",
                        inline=False,
                    )
                    embed.set_footer(
                        text=f"{bot.user}", icon_url=bot.user.display_avatar.url
                    )
                    await mod_log_channel.send(embed=embed)
                    await interaction.send(
                        f"<#{threadinput.id}> has been locked", ephemeral=True
                    )
                    await thread.send("This thread has been locked.")
                else:
                    client = pymongo.MongoClient(LINK)
                    db = client.IGCSEBot
                    locks = db["forumlock"]
                    embed = discord.Embed(
                        description="Instant Forum Lockdown",
                        colour=discord.Colour.green(),
                    )
                    embed.set_author(
                        name=str(interaction.user),
                        icon_url=interaction.user.display_avatar.url,
                    )
                    embed.add_field(
                        name="Unlocked Thread",
                        value=f"<#{threadinput.id}>",
                        inline=False,
                    )
                    embed.add_field(name="Date", value=f"<t:{timenow}:F>", inline=False)
                    embed.add_field(
                        name="ID",
                        value=f"```py\nUser = {interaction.user.id}\nThread = {threadinput.id}```",
                        inline=False,
                    )
                    embed.set_footer(
                        text=f"{bot.user}", icon_url=bot.user.display_avatar.url
                    )
                    await mod_log_channel.send(embed=embed)
                    thread = await thread_id.edit(locked=False)
                    await interaction.send(
                        f"<#{threadinput.id}> has been unlocked", ephemeral=True
                    )
                    await thread.send("This thread has been unlocked.")
                    results = locks.find(
                        {"thread_id": threadinput.id, "resolved": False}
                    )
                    for result in results:
                        try:
                            locks.update_one(
                                {"_id": result["_id"]}, {"$set": {"resolved": True}}
                            )
                        except Exception:
                            print(traceback.format_exc())
    else:
        await interaction.send(f"Please ")

        if action_type == "Channel Lock":
            if channelinput is None:
                await interaction.send(
                    "Please mention the channel in the `channel_name` field.",
                    ephemeral=True,
                )
            else:
                channel = bot.get_channel(channelinput.id)
                overwrite = channel.overwrites_for(interaction.guild.default_role)
                if overwrite.send_messages and overwrite.send_messages_in_threads:
                    overwrite.send_messages = False
                    overwrite.send_messages_in_threads = False
                    embed = discord.Embed(
                        description="Instant Channel Lockdown",
                        colour=discord.Colour.red(),
                    )
                    embed.set_author(
                        name=str(interaction.user),
                        icon_url=interaction.user.display_avatar.url,
                    )
                    embed.add_field(
                        name="Locked Channel",
                        value=f"<#{channelinput.id}>",
                        inline=False,
                    )
                    embed.add_field(name="Date", value=f"<t:{timenow}:F>", inline=False)
                    embed.add_field(
                        name="ID",
                        value=f"```py\nUser = {interaction.user.id}\nChannel = {channelinput.id}```",
                        inline=False,
                    )
                    embed.set_footer(
                        text=f"{bot.user}", icon_url=bot.user.display_avatar.url
                    )
                    await mod_log_channel.send(embed=embed)
                    await channel.set_permissions(
                        interaction.guild.default_role, overwrite=overwrite
                    )
                    await interaction.send(
                        f"<#{channelinput.id}> has been locked", ephemeral=True
                    )
                    await channel.send("This channel has been locked.")
                else:
                    client = pymongo.MongoClient(LINK)
                    db = client.IGCSEBot
                    locks = db["channellock"]
                    overwrite.send_messages = True
                    overwrite.send_messages_in_threads = True
                    embed = discord.Embed(
                        description="Instant Channel Lockdown",
                        colour=discord.Colour.green(),
                    )
                    embed.set_author(
                        name=str(interaction.user),
                        icon_url=interaction.user.display_avatar.url,
                    )
                    embed.add_field(
                        name="Unlocked Channel",
                        value=f"<#{channelinput.id}>",
                        inline=False,
                    )
                    embed.add_field(name="Date", value=f"<t:{timenow}:F>", inline=False)
                    embed.add_field(
                        name="ID",
                        value=f"```py\nUser = {interaction.user.id}\nChannel = {channelinput.id}```",
                        inline=False,
                    )
                    embed.set_footer(
                        text=f"{bot.user}", icon_url=bot.user.display_avatar.url
                    )
                    await mod_log_channel.send(embed=embed)
                    await channel.set_permissions(
                        interaction.guild.default_role, overwrite=overwrite
                    )
                    await interaction.send(
                        f"<#{channelinput.id}> has been unlocked", ephemeral=True
                    )
                    await channel.send("This channel has been unlocked.")
                    results = locks.find(
                        {"channel_id": channelinput.id, "resolved": False}
                    )
                    for result in results:
                        try:
                            locks.update_one(
                                {"_id": result["_id"]}, {"$set": {"resolved": True}}
                            )
                        except Exception:
                            print(traceback.format_exc())


class ChatModerator(discord.ui.Modal):
    def __init__(self):
        super().__init__("Chat Moderator Application", timeout=None)

        self.timezone = discord.ui.TextInput(
            label="Timezone",
            style=discord.TextInputStyle.short,
            placeholder="Please specify your timezone in UTC/GMT time",
            required=True,
        )
        self.add_item(self.timezone)

    async def callback(self, interaction: discord.Interaction):
        chatmod_app_channel = bot.get_channel(
            gpdb.get_pref("chatmod_apps_channel", interaction.guild.id)
        )

        application_embed = discord.Embed(
            title="New application received", color=0xE3FB6D
        )
        application_embed.add_field(name="User", value=interaction.user, inline=False)
        application_embed.add_field(
            name="Position", value="Chat Moderator", inline=False
        )
        application_embed.add_field(
            name="Timezone", value=self.timezone.value, inline=False
        )

        await chatmod_app_channel.send(embed=application_embed)
        await interaction.send(
            "Thank you for applying. If you are selected as a Chat Moderator, we will send you a modmail with more information. Good luck!",
            ephemeral=True,
        )


class ApplyDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label="Chat Moderator",
                description="Apply for the chat moderator position",
                emoji="💬",
            )
        ]
        super().__init__(
            placeholder="Select the application type",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "Chat Moderator":
            chat_modal = ChatModerator()
            await interaction.response.send_modal(modal=chat_modal)


@bot.slash_command(
    name="apply", description="Apply for positions in the Discord server"
)
async def apply(interaction: discord.Interaction):
    view = discord.ui.View()
    view.add_item(ApplyDropdown())
    await interaction.send(view=view, ephemeral=True)


class NewEmbed(discord.ui.Modal):
    def __init__(
        self,
        embed: discord.Embed,
        embed_msg: discord.Message = None,
        content: str = None,
        channel: discord.TextChannel = None,
    ):
        self.embed = embed
        self.msg = embed_msg
        self.content = content
        self.channel = channel

        super().__init__("New embed!", timeout=None)

        self.name = discord.ui.TextInput(
            label="Title of the embed",
            style=discord.TextInputStyle.short,
            placeholder="This will be the title of the embed",
            required=True,
        )
        self.add_item(self.name)

        self.description = discord.ui.TextInput(
            label="Description of the embed",
            style=discord.TextInputStyle.paragraph,
            placeholder="This will be the description of the embed",
            required=True,
        )
        self.add_item(self.description)

    async def callback(self, interaction: discord.Interaction) -> None:
        self.embed.title = self.name.value
        self.embed.description = self.description.value
        if self.msg:
            await self.msg.edit(content=self.content, embed=self.embed)
        else:
            await self.channel.send(content=self.content, embed=self.embed)
        await interaction.send("Done!", ephemeral=True, delete_after=1)


@bot.slash_command(description="send and edit embeds (for mods)")
async def embed(
    interaction: discord.Interaction,
    channel: discord.abc.GuildChannel = discord.SlashOption(
        name="channel",
        description="Default is the channel you use the command in",
        channel_types=[discord.ChannelType.text],
        required=False,
    ),
    content: str = discord.SlashOption(
        name="content", description="The content of the embed", required=False
    ),
    colour: str = discord.SlashOption(
        name="colour",
        description="The hexadecimal colour code for the embed (Default is green)",
        required=False,
    ),
    message_id: str = discord.SlashOption(
        name="message_id",
        description="The id of the message embed you want to edit",
        required=False,
    ),
):

    if not await is_moderator(interaction.user):
        await interaction.send(
            "You do not have the necessary permissions to perform this action",
            ephemeral=True,
        )
        return
    if channel:
        embed_channel = channel
    else:
        embed_channel = interaction.channel
    if message_id:
        embed_message = await embed_channel.fetch_message(int(message_id))
        previous_embed = embed_message.embeds[0]
        embed = discord.Embed(
            colour=previous_embed.colour,
            title=previous_embed.title,
            description=previous_embed.description,
        )
    else:
        embed = discord.Embed()
        embed_message = None
    if colour:
        try:
            embed.colour = int(colour[1:], 16)
        except Exception:
            await interaction.send("Invalid Hex code", ephemeral=True)
            return
    else:
        embed.colour = discord.Colour.green()
    modal = NewEmbed(embed, embed_message, content, embed_channel)
    await interaction.response.send_modal(modal)


@bot.slash_command(description="Make an anonymous confession.")
async def confess(
    interaction: discord.Interaction,
    confession: str = discord.SlashOption(
        name="confession",
        description="Write your confession and it will be sent anonymously",
        required=True,
    ),
):

    approval_channel = bot.get_channel(
        gpdb.get_pref("confession_approval_channel", interaction.guild.id)
    )
    confession_channel = bot.get_channel(
        gpdb.get_pref("anon_confession_channel", interaction.guild.id)
    )

    view = discord.ui.View(timeout=None)
    approveBTN = discord.ui.Button(label="Approve", style=discord.ButtonStyle.blurple)
    rejectBTN = discord.ui.Button(label="Reject", style=discord.ButtonStyle.red)

    async def ApproveCallBack(interaction):
        embed = discord.Embed(colour=discord.Colour.green(), description=confession)
        embed.set_author(
            name=f"Approved by {interaction.user}",
            icon_url=interaction.user.display_avatar.url,
        )
        await interaction.edit(embed=embed, view=None)
        embed = discord.Embed(colour=discord.Colour.random(), description=confession)
        await confession_channel.send(content="New Anonymous Confession", embed=embed)

    approveBTN.callback = ApproveCallBack

    async def RejectCallBack(interaction):
        embed = discord.Embed(colour=discord.Colour.red(), description=confession)
        embed.set_author(
            name=f"Rejected by {interaction.user}",
            icon_url=interaction.user.display_avatar.url,
        )
        await interaction.edit(embed=embed, view=None)

    rejectBTN.callback = RejectCallBack

    view.add_item(approveBTN)
    view.add_item(rejectBTN)
    embed = discord.Embed(colour=discord.Colour.random(), description=confession)
    await approval_channel.send(embed=embed, view=view)
    await interaction.send(
        "Your confession has been sent to the moderators.\nYou have to wait for their approval.",
        ephemeral=True,
    )


class Level(discord.ui.Select):
    def __init__(self):
        options = []
        for group in subreddits.keys():
            options.append(discord.SelectOption(label=group))
        super().__init__(
            placeholder="Choose a level...",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        self.view.clear_items()
        self.view.add_item(Groups(self.values[0]))
        await interaction.response.edit_message(view=self.view)


class Groups(discord.ui.Select):
    def __init__(self, level):
        options = []
        self.level = level
        for group in subreddits[level].keys():
            options.append(discord.SelectOption(label=group))
        super().__init__(
            placeholder="Choose a subject group...",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        group = self.values[0]
        view = discord.ui.View(timeout=None)
        for subject in subreddits[self.level][group].keys():
            view.add_item(
                discord.ui.Button(
                    label=subject,
                    style=discord.ButtonStyle.url,
                    url=subreddits[self.level][group][subject],
                )
            )
        await interaction.response.edit_message(view=view)


class DropdownView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Level())


@bot.slash_command(description="View the r/igcse resources repository")
async def resources(interaction: discord.Interaction):
    await interaction.send(view=DropdownView())


class EditMessage(discord.ui.Modal):
    def __init__(self, channel: discord.abc.GuildChannel):
        self.channel = channel
        super().__init__("Edit a message!", timeout=None)

        self.message_id = discord.ui.TextInput(
            label="Message ID",
            style=discord.TextInputStyle.short,
            placeholder="ID of the message you want to edit",
            required=True,
        )
        self.add_item(self.message_id)

        self.message_content = discord.ui.TextInput(
            label="Content",
            style=discord.TextInputStyle.paragraph,
            placeholder="The main body of the message you wish to send",
            required=True,
        )
        self.add_item(self.message_content)

    async def callback(self, interaction: discord.Interaction):
        try:
            message = await self.channel.fetch_message(int(self.message_id.value))
            await message.edit(self.message_content.value)
            await interaction.send("Message edited!", ephemeral=True)
        except Exception:
            await interaction.send(
                "Message ID has to be an integer and has to be in the channel chosen!",
                ephemeral=True,
            )


class SendMessage(discord.ui.Modal):
    def __init__(self, channel: discord.abc.GuildChannel):
        self.channel = channel
        super().__init__("Send a message!", timeout=None)

        self.message_id = discord.ui.TextInput(
            label="Message ID",
            style=discord.TextInputStyle.short,
            placeholder="ID of the message you want to reply to",
            required=False,
        )
        self.add_item(self.message_id)

        self.message_content = discord.ui.TextInput(
            label="Content",
            style=discord.TextInputStyle.paragraph,
            placeholder="The body of the message you wish to send",
            required=True,
        )
        self.add_item(self.message_content)

    async def callback(self, interaction: discord.Interaction):
        if self.message_id.value:
            try:
                message = await self.channel.fetch_message(int(self.message_id.value))
                await message.reply(self.message_content.value)
                await interaction.send("Message sent!", ephemeral=True)
            except Exception:
                await interaction.send(
                    "Message ID has to be an integer and has to be in the channel chosen!",
                    ephemeral=True,
                )
        else:
            await self.channel.send(self.message_content.value)
            await interaction.send("Message sent!", ephemeral=True)


@bot.slash_command(name="message", description="Sends or Edits a Message (for mods)")
async def send_editcommand(
    interaction: discord.Interaction,
    action_type: str = discord.SlashOption(
        name="action_type",
        description="SEND or EDIT?",
        choices=["Send Message", "Edit Message"],
        required=True,
    ),
    channel: discord.TextChannel = discord.SlashOption(
        name="channel",
        description="The channel to send the message to or where the message is located",
        required=False,
    ),
):

    if not await is_moderator(interaction.user):
        await interaction.send(
            "You are not authorized to perform this action.", ephemeral=True
        )
        return
    if channel is None:
        channel = interaction.channel
    if action_type == "Send Message":
        await interaction.response.send_modal(modal=SendMessage(channel))
    if action_type == "Edit Message":
        await interaction.response.send_modal(modal=EditMessage(channel))


bot.run(TOKEN)
