from constants import TOKEN, LINK, GUILD_ID, LOG_CHANNEL_ID, CREATE_DM_CHANNEL_ID, WELCOME_CHANNEL_ID, SUBJECT_ROLES, SESSION_ROLES, MODLOG_CHANNEL_ID, IGCSE_SUBJECT_CODES, ALEVEL_SUBJECT_CODES
from bot import discord, bot, keywords, typing, tasks, commands, requests, json, time, datetime, pymongo
from data import reactionroles_data, helper_roles, subreddits, study_roles
import ast
import random 
#git


# events
import on_ready
import on_command_error
import on_application_command_error
import on_message
import on_voice_state_update
import on_raw_reaction_add
import on_raw_reaction_remove
import on_thread_join
import on_guild_join
import on_auto_moderation_action_execution

# mongo
from db import gpdb, rrdb, kwdb, repdb

# utility
from roles import has_role, get_role, is_moderator, is_moderator, is_server_booster, is_helper
from bans import is_banned

@bot.event
async def on_member_join(member: discord.Member):
    if member.guild.id == GUILD_ID: 
        embed = discord.Embed.from_dict(eval(r"""{'color': 3066993, 'type': 'rich', 'description': "Hello and welcome to the official r/IGCSE Discord server, a place where you can ask any doubts about your exams and find help in a topic you're struggling with! We strongly suggest you read the following message to better know how our server works!\n\n***How does the server work?***\n\nThe server mostly entirely consists of the students who are doing their IGCSE and those who have already done their IGCSE exams. This server is a place where you can clarify any of your doubts regarding how exams work as well as any sort of help regarding a subject or a topic in which you struggle.\n\nDo be reminded that academic dishonesty is not allowed in this server and you may face consequences if found to be doing so. Examples of academic dishonesty are listed below (the list is non-exhaustive) - by joining the server you agree to follow the rules of the server.\n\n> Asking people to do your homework for you, sharing any leaked papers before the exam session has ended, etc.), asking for leaked papers or attempted malpractice are not allowed as per *Rule 1*. \n> \n> Posting pirated content such as textbooks or copyrighted material are not allowed in this server as per *Rule 7.*\n\n***How to ask for help?***\n\nWe have subject helpers for every subject to clear any doubts or questions you may have. If you want a subject helper to entertain a doubt, you should use the command `/helper` in the respective subject channel. A timer of **15 minutes** will start before the respective subject helper will be pinged. Remember to cancel your ping once a helper is helping you!\n\n***How to contact the moderators?***\n\nYou can contact us by sending a message through <@861445044790886467> by responding to the bot, where it will be forwarded to the moderators to view. Do be reminded that only general server inquiries should be sent and other enquiries will not be entertained, as there are subject channels for that purpose.", 'title': 'Welcome to r/IGCSE!'}"""))
        channel = await member.create_dm()
        await channel.send(embed=embed)
        welcome = bot.get_channel(WELCOME_CHANNEL_ID)
        await welcome.send(f"Welcome {member.mention}! Pick up your subject roles from <id:customize> to get access to subject channels and resources!")

class DropdownRR(discord.ui.Select):
    def __init__(self, category, options):
        self._options = options
        selectOptions = [
            discord.SelectOption(emoji=option[0], label=option[1], value=option[2]) for option in options
        ]
        if category == "Colors":
            super().__init__(placeholder="Select your Color", min_values=0, max_values=1, options=selectOptions)
        else:
            super().__init__(placeholder=f"Select your {category}", min_values=0, max_values=len(selectOptions), options=selectOptions)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        added_role_names = []
        removed_role_names = []
        for option in self._options:
            role = interaction.guild.get_role(int(option[2]))
            if str(option[2]) in self.values:
                if role not in interaction.user.roles:
                    await interaction.user.add_roles(role)
                    added_role_names.append(role.name)
            else:
                if role in interaction.user.roles:
                    await interaction.user.remove_roles(role)
                    removed_role_names.append(role.name)
        if len(added_role_names) > 0 and len(removed_role_names) > 0:
            await interaction.send(
                f"Successfully opted for roles: {', '.join(added_role_names)} and unopted from roles: {', '.join(removed_role_names)}.", ephemeral=True)
        elif len(added_role_names) > 0 and len(removed_role_names) == 0:
            await interaction.send(f"Successfully opted for roles: {', '.join(added_role_names)}.", ephemeral=True)
        elif len(added_role_names) == 0 and len(removed_role_names) > 0:
            await interaction.send(f"Successfully unopted from roles: {', '.join(removed_role_names)}.", ephemeral=True)


class DropdownViewRR(discord.ui.View):
    def __init__(self, roles_type):
        super().__init__(timeout=None)

        for category, options in reactionroles_data[roles_type].items():
            self.add_item(DropdownRR(category, options))

class RolePickerCategories(discord.ui.Select):
    def __init__(self):
        options = ["Subject Roles", "Session Roles", "Study Ping Roles", "Server Roles"]
        super().__init__(
            placeholder="Choose a roles category...",
            min_values=1,
            max_values=1,
            options=[discord.SelectOption(label=option) for option in options],
            row=0
        )

    async def callback(self, interaction: discord.Interaction):
        roles_type = self.values[0]
        view = DropdownViewRR(roles_type)
        await interaction.response.edit_message(content=f"Choose your {roles_type}", view=view)

class RolePickerCategoriesView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(RolePickerCategories())

    @discord.ui.button(label="Remove all Roles", style=discord.ButtonStyle.red, row=1)
    async def remove_roles_btn(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        removed_role_names = []
        for category in reactionroles_data.values():
            for options in category.values():
                for option in options:
                    role = interaction.guild.get_role(int(option[2]))
                    if role in interaction.user.roles:
                        await interaction.user.remove_roles(role)
                        removed_role_names.append(role.name)
        if len(removed_role_names) > 0:
            await interaction.send(f"Successfully unopted from roles: {', '.join(removed_role_names)}.", ephemeral=True)
        else:
            await interaction.send("No roles to remove! Please pick up roles first.", ephemeral=True)


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
        super().__init__("Execute a piece of code!", timeout = None)

        self.cmd = discord.ui.TextInput(
            label = "Code",
            style = discord.TextInputStyle.paragraph,
            placeholder = "Enter the code that is to be executed over here",
            required = True,
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

        result = (await eval(f"{fn_name}()", env))
        await interaction.send(result)

@bot.slash_command(name="eval", description="Evaluate a piece of code.", guild_ids=[GUILD_ID])
async def _eval(interaction: discord.Interaction):
    if not await is_moderator(interaction.user):
        await interaction.send("This is not for you.", ephemeral=True)
        return
    eval_modal = EvalModal()
    await interaction.response.send_modal(eval_modal)


@bot.slash_command(description="Pick up your roles", guild_ids=[GUILD_ID])
async def roles(interaction: discord.Interaction):
    await interaction.send(view=RolePickerCategoriesView(), ephemeral=True)


@bot.command(description="Dropdown for picking up reaction roles", guild_ids=[GUILD_ID])
async def roles(ctx):
    await ctx.send(view=RolePickerCategoriesView())

@bot.command(description="Create reaction roles", guild_ids=[GUILD_ID])
async def rrmake(ctx):
    if await is_moderator(ctx.author):
        guild = bot.get_guild(GUILD_ID)
        while True:
            await ctx.send("Enter the link/id of the message to which the reaction roles must be added")
            msg_link = await bot.wait_for("message", check = lambda m: m.author == ctx.author and m.channel == ctx.channel)
            link = str(msg_link.content)
            try:
                msg_id = int(link.split("/")[-1])
                try:
                    reaction_msg = await ctx.fetch_message(msg_id)
                    break
                except discord.NotFound:
                    await ctx.send("Invalid message")
            except ValueError:
                await ctx.send("Invalid input")
        await ctx.send("Now, enter the reactions and their corresponding roles in the following format: `<Emoji> <@Role>`. Type 'stop' when you are done")
        rrs = []
        while True:
            rr_msg = await bot.wait_for("message", check = lambda m: m.author == ctx.author and m.channel == ctx.channel)
            rr = str(rr_msg.content).lower()
            if rr == "stop":
                break
            try:
                reaction, role = rr.split()
            except ValueError:
                await ctx.send("You have to enter a reaction followed by a role separated by a space")
            else:
                try:
                    int(role[3:-1])
                except ValueError:
                    await ctx.send("Invalid input")
                else:
                    if guild.get_role(int(role[3:-1])) is None:
                        await ctx.send("Invalid input")
                    else:
                        rrs.append([reaction, int(role[3:-1])])
                        await rr_msg.add_reaction("✅")
        for x in rrs:
            await reaction_msg.add_reaction(x[0])
            data = x.copy()
            data.append(msg_id)
            rrdb.new_rr(data)
        await ctx.send("Reactions added!")
                
@bot.slash_command(name = "rrmake", description = "Create reaction roles", guild_ids = [GUILD_ID])
async def rrmake(interaction: discord.Interaction, link: str = discord.SlashOption(name = "link", description = "The link/id of the message to which the reaction roles will be added", required = True)):
    if await is_moderator(interaction.user):
        guild = bot.get_guild(GUILD_ID)
        channel = interaction.channel
        try:
            msg_id = int(link.split("/")[-1])
            try:
                reaction_msg = await channel.fetch_message(msg_id)
            except discord.NotFound:
                await interaction.send("Invalid message", ephemeral = True)
            else:
                await interaction.send("Now, enter the reactions and their corresponding roles in the following format: `<Emoji> <@Role>`. Type 'stop' when you are done")
                rrs = []
                while True:
                    rr_msg = await bot.wait_for("message", check = lambda m: m.author == interaction.user and m.channel == channel)
                    rr = str(rr_msg.content).lower()
                    if rr == "stop":
                        break
                    try:
                        reaction, role = rr.split()
                    except ValueError:
                        await channel.send("You have to enter a reaction followed by a role separated by a space")
                    else:
                        try:
                            int(role[3:-1])
                        except ValueError:
                            await channel.send("Invalid input")
                        else:
                            if guild.get_role(int(role[3:-1])) is None:
                                await channel.send("Invalid input")
                            else:
                                rrs.append([reaction, int(role[3:-1])])
                                await rr_msg.add_reaction("✅")
                for x in rrs:
                    await reaction_msg.add_reaction(x[0])
                    data = x.copy()
                    data.append(msg_id)
                    rrdb.new_rr(data)
                await channel.send("Reactions added!")
        except ValueError:
            await interaction.send("Invalid input", ephemeral = True)

@bot.slash_command(description="Choose a display colour for your name", guild_ids=[GUILD_ID])
async def colorroles(interaction: discord.Interaction):
    if await is_moderator(interaction.user) or await is_server_booster(interaction.user) or await has_role(interaction.user, "100+ Rep Club"):
        await interaction.send(view=DropdownViewRR('Color Roles'), ephemeral=True)
    else:
        await interaction.send("This command is only available for Server Boosters and 100+ Rep Club members", ephemeral=True)


@bot.command(description="Choose a display colour for your name", guild_ids=[GUILD_ID])
async def colorroles(ctx):
    if await is_moderator(ctx.author) or await is_server_booster(ctx.author) or await has_role(ctx.author, "100+ Rep Club"):
        await ctx.send(view=DropdownViewRR('Color Roles'))
    else:
        await ctx.send("This command is only available for Server Boosters and 100+ Rep Club members")


# Suggestions

@bot.slash_command(description="Create a new in-channel poll")
async def yesnopoll(interaction: discord.Interaction, poll: str = discord.SlashOption(name="poll", description="The poll to be created", required=True)):
    embed = discord.Embed(title=poll, description=f"Total Votes: 0\n\n{'🟩' * 10}\n\n(from: {interaction.user})", colour=discord.Colour.purple())
    await interaction.send("Creating Poll.", ephemeral=True)
    msg1 = await interaction.channel.send(embed=embed)
    await msg1.add_reaction('✅')
    await msg1.add_reaction('❌')

class CancelPingBtn(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=890)
        self.value = True

    @discord.ui.button(label="Cancel Ping", style=discord.ButtonStyle.blurple)
    async def cancel_ping_btn(self, button: discord.ui.Button, interaction_b: discord.Interaction):
        if (interaction_b.user != self.user) and (not await is_helper(interaction_b.user)) and (not await is_moderator(interaction_b.user)):
            await interaction_b.send("You do not have permission to do this.", ephemeral=True)
            return
        button.disabled = True
        self.value = False
        await self.message.edit(content=f"Ping cancelled by {interaction_b.user}", embed=None, view=None)

    async def on_timeout(self): # 15 minutes has passed so execute the ping.
        await self.message.edit(view=None) # Remove Cancel Ping button
        if self.value:
            if self.message_id:
                url = f"https://discord.com/channels/{self.guild.id}/{self.channel.id}/{self.message_id}"
                embed = discord.Embed(description=f"[Jump to the message.]({url})")
            else:
                embed = discord.Embed()
            embed.set_author(name=str(self.user), icon_url=self.user.display_avatar.url)
            await self.message.channel.send(self.helper_role.mention, embed=embed)  # Execute ping
            await self.message.delete()  # Delete original message


@bot.slash_command(description="Ping a helper in any subject channel", guild_ids=[GUILD_ID])
async def helper(interaction: discord.Interaction, message_id: str = discord.SlashOption(name="message_id", description="The ID of the message containing the question.", required=False)):
    if message_id:
        try:
            message_id = int(message_id)
        except ValueError:
            await interaction.send("The provided message ID is invalid.", ephemeral=True)
            return
    try:
        helper_role = discord.utils.get(interaction.guild.roles, id=helper_roles[interaction.channel.id])
    except:
        await interaction.send("There are no helper roles specified for this channel.", ephemeral=True)
        return
    await interaction.response.defer()
    roles = [role.name.lower() for role in interaction.user.roles]
    if "server booster" in roles:
        if message_id:
            url = f"https://discord.com/channels/{interaction.guild.id}/{interaction.channel.id}/{message_id}"
            embed = discord.Embed(description=f"[Jump to the message.]({url})")
        else:
            embed = discord.Embed()
        embed.set_author(name=str(interaction.user), icon_url=interaction.user.display_avatar.url)
        await interaction.send(helper_role.mention, embed=embed)
        return
    view = CancelPingBtn()
    embed = discord.Embed(description=f"The helper role for this channel, `@{helper_role.name}`, will automatically be pinged (<t:{int(time.time() + 890)}:R>).\nIf your query has been resolved by then, please click on the `Cancel Ping` button.")
    embed.set_author(name=str(interaction.user), icon_url=interaction.user.display_avatar.url)
    message = await interaction.send(embed=embed, view=view)
    view.message = message
    view.channel = interaction.channel
    view.guild = interaction.guild
    view.message_id = message_id
    view.helper_role = helper_role
    view.user = interaction.user


@bot.command(name="refreshhelpers", description="Refresh the helper count in the description of subject channels",
             guild_ids=[GUILD_ID])
async def refreshhelpers(ctx):
    changed = []
    for chnl, role in helper_roles.items():
        try:
            helper_role = discord.utils.get(ctx.message.guild.roles, id=role)
            no_of_users = len(helper_role.members)
            channel = bot.get_channel(chnl)
            new_topic = None
            for line in channel.topic.split("\n"):
                if "No. of helpers" in line:
                    new_topic = channel.topic.replace(line, f"No. of helpers: {no_of_users}")
                    break
            else:
                new_topic = f"{channel.topic}\nNo. of helpers: {no_of_users}"
            if channel.topic != new_topic:
                await channel.edit(topic=new_topic)
                changed.append(channel.mention)
        except:
            continue
    if changed:
        await ctx.message.reply("Done! Changed channels: " + ", ".join(changed))
    else:
        await ctx.message.reply("No changes were made.")


@bot.slash_command(description="View someone's current rep")
async def rep(interaction: discord.Interaction,
              user: discord.User = discord.SlashOption(name="user", description="User to view rep of", required=False)):
    await interaction.response.defer()
    if user is None:
        user = interaction.user
    rep = repdb.get_rep(user.id, interaction.guild.id)
    if rep is None:
        rep = 0
    await interaction.send(f"{user} has {rep} rep.", ephemeral=False)


@bot.slash_command(description="Change someone's current rep (for mods)")
async def change_rep(interaction: discord.Interaction, user: discord.User = discord.SlashOption(name="user", description="User to view rep of", required=True), new_rep: int = discord.SlashOption(name="new_rep", description="New rep amount", required=True, min_value=0, max_value=9999)):
    if await is_moderator(interaction.user):
        await interaction.response.defer()
        rep = repdb.change_rep(user.id, new_rep, interaction.guild.id)
        await interaction.send(f"{user} now has {rep} rep.", ephemeral=False)
    else:
        await interaction.send("You are not authorized to use this command.", ephemeral=True)


@bot.slash_command(description="View the current rep leaderboard")
async def leaderboard(interaction: discord.Interaction, page: int = discord.SlashOption(name="page", description="Page number to to display", required=False, min_value=1, max_value=99999), user_to_find: discord.User = discord.SlashOption(name="user", description="User to find on the leaderboard", required=False)):
    await interaction.response.defer()
    leaderboard = repdb.rep_leaderboard(interaction.guild.id)  # Rep leaderboard
    leaderboard = [item.values() for item in leaderboard]  # Changing format of leaderboard
    chunks = [list(leaderboard)[x:x + 9] for x in range(0, len(leaderboard), 9)]  # Split into groups of 9
    pages = []
    for n, chunk in enumerate(chunks):
        embed = discord.Embed(title="Reputation Leaderboard", description=f"Page {n + 1} of {len(chunks)}", colour=discord.Colour.green())
        for user, rep in chunk:
            if user_to_find:
                if user_to_find.id == user:
                    page = n + 1
            user_name = interaction.guild.get_member(user)
            if rep == 0 or user_name is None:
                repdb.delete_user(user, interaction.guild.id)
            else:
                embed.add_field(name=user_name, value=str(rep) + "\n", inline=True)
        pages.append(embed)

    if not page: page = 1

    first, prev = discord.ui.Button(emoji="⏪", style=discord.ButtonStyle.blurple), discord.ui.Button(emoji="⬅️", style=discord.ButtonStyle.blurple)
    if page == 1:
        first.disabled, prev.disabled = True, True

    nex, last = discord.ui.Button(emoji="➡️", style=discord.ButtonStyle.blurple), discord.ui.Button(emoji="⏩", style=discord.ButtonStyle.blurple)
    view = discord.ui.View(timeout=120)


    async def timeout():
        nonlocal message
        disabled = discord.ui.View()
        for b in view.children:
            d = b
            d.disabled = True
            disabled.add_item(d)
        await message.edit(view=disabled)
    view.on_timeout = timeout

    async def f_callback(b_interaction):
        if b_interaction.user != interaction.user:
            await b_interaction.response.send_message("This is not for you.", ephemeral=True)
            return
        nonlocal page
        view = discord.ui.View(timeout=None)
        first.disabled, prev.disabled, nex.disabled, last.disabled = True, True, False, False
        view.add_item(first); view.add_item(prev); view.add_item(nex); view.add_item(last)
        page = 1
        await b_interaction.response.edit_message(embed=pages[page - 1], view=view)

    async def p_callback(b_interaction):
        if b_interaction.user != interaction.user:
            await b_interaction.response.send_message("This is not for you.", ephemeral=True)
            return
        nonlocal page
        page -= 1
        view = discord.ui.View(timeout=None)
        if page == 1:
            first.disabled, prev.disabled, nex.disabled, last.disabled = True, True, False, False
        else:
            first.disabled, prev.disabled, nex.disabled, last.disabled = False, False, False, False
        view.add_item(first); view.add_item(prev); view.add_item(nex); view.add_item(last)
        await b_interaction.response.edit_message(embed=pages[page - 1], view=view)

    async def n_callback(b_interaction):
        if b_interaction.user != interaction.user:
            await b_interaction.response.send_message("This is not for you.", ephemeral=True)
            return
        nonlocal page
        page += 1
        view = discord.ui.View(timeout=None)
        if page == len(pages):
            first.disabled, prev.disabled, nex.disabled, last.disabled = False, False, True, True
        else:
            first.disabled, prev.disabled, nex.disabled, last.disabled = False, False, False, False
        view.add_item(first); view.add_item(prev); view.add_item(nex); view.add_item(last)
        await b_interaction.response.edit_message(embed=pages[page - 1], view=view)

    async def l_callback(b_interaction):
        if b_interaction.user != interaction.user:
            await b_interaction.response.send_message("This is not for you.", ephemeral=True)
            return
        nonlocal page
        view = discord.ui.View(timeout=None)
        first.disabled, prev.disabled, nex.disabled, last.disabled = False, False, True, True
        view.add_item(first); view.add_item(prev); view.add_item(nex); view.add_item(last)
        page = len(pages)
        await b_interaction.response.edit_message(embed=pages[page - 1], view=view)

    first.callback, prev.callback, nex.callback, last.callback = f_callback, p_callback, n_callback, l_callback
    view.add_item(first); view.add_item(prev); view.add_item(nex); view.add_item(last)

    message = await interaction.send(embed=pages[page - 1], view=view)

class AddKeywords(discord.ui.Modal):
    def __init__(self):
        super().__init__("Add a keyword", timeout=None)

        self.keyword = discord.ui.TextInput(label="Add keyword", style=discord.TextInputStyle.short, placeholder="The keyword you would like to add", required=True)
        self.autoresponse = discord.ui.TextInput(label="Add response", style=discord.TextInputStyle.paragraph, placeholder="The response you would like to be sent", required=True)

        self.add_item(self.keyword)
        self.add_item(self.autoresponse)
    
    async def callback(self, interaction: discord.Interaction):
        kwdb.add_keyword(self.keyword.value, self.autoresponse.value, interaction.guild.id)
        keywords[interaction.guild.id] = kwdb.get_keywords(interaction.guild.id)
        await interaction.send(f"Created keyword `{self.keyword.value}` for autoresponse `{self.autoresponse.value}`", ephemeral=True, delete_after=2)

@bot.slash_command(description="Add keywords (for mods)")
async def add_keyword(interaction: discord.Interaction):
    if not await is_moderator(interaction.user):
        return await interaction.send("You do not have the permissions to perform this action")
    await interaction.response.send_modal(modal=AddKeywords())

@bot.slash_command(description="Delete keywords (for mods)")
async def delete_keyword(interaction: discord.Interaction, keyword: str = discord.SlashOption(name="keyword", description="Keyword to delete", required=True)):
    if not await is_moderator(interaction.user):
        return await interaction.send("You do not have the permissions to perform this action")
    kwdb.remove_keyword(keyword, interaction.guild.id)
    keywords[interaction.guild.id] = kwdb.get_keywords(interaction.guild.id)
    await interaction.send(f"Deleted keyword `{keyword}`", ephemeral=True, delete_after=2)

@bot.slash_command(description="Display all keywords")
async def list_keywords(interaction: discord.Interaction):
    page = 1
    
    await interaction.response.defer()
    keywords = kwdb.keyword_list(interaction.guild.id)  # List of keywords
    keywords = [item.values() for item in keywords]  # Changing format of keywords
    chunks = [list(keywords)[x:x + 9] for x in range(0, len(keywords), 9)]  # Split into groups of 9

    pages = []
    for n, chunk in enumerate(chunks):
        embed = discord.Embed(title="List of keywords", description=f"Page {n + 1} of {len(chunks)}", colour=discord.Colour.green())
        for keyword, autoresponse in chunk:
            embed.add_field(name=keyword, value="" + "\n", inline=True)
        pages.append(embed)

    if not page: page = 1

    first, prev = discord.ui.Button(emoji="⏪", style=discord.ButtonStyle.blurple), discord.ui.Button(emoji="⬅️", style=discord.ButtonStyle.blurple)

    nex, last = discord.ui.Button(emoji="➡️", style=discord.ButtonStyle.blurple), discord.ui.Button(emoji="⏩", style=discord.ButtonStyle.blurple)
    if page == 1:
        first.disabled, prev.disabled = True, True
    view = discord.ui.View(timeout=120)


    async def timeout():
        nonlocal message
        disabled = discord.ui.View()
        for b in view.children:
            d = b
            d.disabled = True
            disabled.add_item(d)
        await message.edit(view=disabled)
    view.on_timeout = timeout

    async def f_callback(b_interaction):
        if b_interaction.user != interaction.user:
            await b_interaction.response.send_message("This is not for you.", ephemeral=True)
            return
        nonlocal page
        view = discord.ui.View(timeout=None)
        first.disabled, prev.disabled, nex.disabled, last.disabled = True, True, False, False
        view.add_item(first); view.add_item(prev); view.add_item(nex); view.add_item(last)
        page = 1
        await b_interaction.response.edit_message(embed=pages[page - 1], view=view)

    async def p_callback(b_interaction):
        if b_interaction.user != interaction.user:
            await b_interaction.response.send_message("This is not for you.", ephemeral=True)
            return
        nonlocal page
        page -= 1
        view = discord.ui.View(timeout=None)
        if page == 1:
            first.disabled, prev.disabled, nex.disabled, last.disabled = True, True, False, False
        else:
            first.disabled, prev.disabled, nex.disabled, last.disabled = False, False, False, False
        view.add_item(first); view.add_item(prev); view.add_item(nex); view.add_item(last)
        await b_interaction.response.edit_message(embed=pages[page - 1], view=view)

    async def n_callback(b_interaction):
        if b_interaction.user != interaction.user:
            await b_interaction.response.send_message("This is not for you.", ephemeral=True)
            return
        nonlocal page
        page += 1
        view = discord.ui.View(timeout=None)
        if page == len(pages):
            first.disabled, prev.disabled, nex.disabled, last.disabled = False, False, True, True
        else:
            first.disabled, prev.disabled, nex.disabled, last.disabled = False, False, False, False
        view.add_item(first); view.add_item(prev); view.add_item(nex); view.add_item(last)
        await b_interaction.response.edit_message(embed=pages[page - 1], view=view)

    async def l_callback(b_interaction):
        if b_interaction.user != interaction.user:
            await b_interaction.response.send_message("This is not for you.", ephemeral=True)
            return
        nonlocal page
        view = discord.ui.View(timeout=None)
        first.disabled, prev.disabled, nex.disabled, last.disabled = False, False, True, True
        view.add_item(first); view.add_item(prev); view.add_item(nex); view.add_item(last)
        page = len(pages)
        await b_interaction.response.edit_message(embed=pages[page - 1], view=view)

    first.callback, prev.callback, nex.callback, last.callback = f_callback, p_callback, n_callback, l_callback
    view.add_item(first); view.add_item(prev); view.add_item(nex); view.add_item(last)

    message = await interaction.send(embed=pages[page - 1], view=view)

# Misc Functions

@bot.command(description="Clear messages in a channel")
async def clear(ctx, num_to_clear: int):
    if not await is_moderator(ctx.author):
        await ctx.reply("You do not have the permissions to perform this action.")
        return
    try:
        await ctx.channel.purge(limit=num_to_clear + 1)
    except:
        await ctx.reply("Oops! I can only delete messages sent in the last 14 days")

class SendMessage(discord.ui.Modal):
    def __init__(self, channel: discord.abc.GuildChannel):
        self.channel = channel
        super().__init__("Send a message!", timeout = None)

        self.message_id = discord.ui.TextInput(
            label = "Message ID",
            style = discord.TextInputStyle.short,
            placeholder = "ID of the message you want to reply to",
            required = False
        )
        self.add_item(self.message_id)

        self.message_content = discord.ui.TextInput(
            label = "Content",
            style = discord.TextInputStyle.paragraph,
            placeholder = "The body of the message you wish to send",
            required = True
        )
        self.add_item(self.message_content)
    
    async def callback(self, interaction: discord.Interaction):
        if self.message_id.value:
            try:
                message = await self.channel.fetch_message(int(self.message_id.value))
                await message.reply(self.message_content.value)
                await interaction.send("Message sent!", ephemeral = True)
            except:
                await interaction.send("Message ID has to be an integer and has to be in the channel chosen!", ephemeral = True)
        else:
            await self.channel.send(self.message_content.value)
            await interaction.send("Message sent!", ephemeral = True)

@bot.slash_command(description="Send messages using the bot (for mods)")
async def send_message(interaction: discord.Interaction, channel_to_send_to: discord.abc.GuildChannel = discord.SlashOption(name="channel_to_send_to", description="Channel to send the message to", required=True)):
    if not await is_moderator(interaction.user):
        await interaction.send("You are not authorized to perform this action.")
        return
    await interaction.response.send_modal(modal = SendMessage(channel_to_send_to))

@bot.command(description="Send messages using the bot (for mods)")
async def send_message(ctx, message_text: str, channel_to_send_to: typing.Optional[discord.abc.GuildChannel], message_to_reply_to: typing.Optional[discord.Message]):
    if not await is_moderator(ctx.author):
        await ctx.send("You are not authorized to perform this action.")
        return
    if message_to_reply_to:
        await message_to_reply_to.reply(message_text)
        await ctx.send("Done!")
    else:
        await channel_to_send_to.send(message_text)
        await ctx.send("Done!")

class EditMessage(discord.ui.Modal):
    def __init__(self, channel: discord.abc.GuildChannel):
        self.channel = channel
        super().__init__("Edit a message!", timeout = None)

        self.message_id = discord.ui.TextInput(
            label = "Message ID",
            style = discord.TextInputStyle.short,
            placeholder = "ID of the message you want to edit",
            required = True
        )
        self.add_item(self.message_id)

        self.message_content = discord.ui.TextInput(
            label = "Content",
            style = discord.TextInputStyle.paragraph,
            placeholder = "The main body of the message you wish to send",
            required = True
        )
        self.add_item(self.message_content)
    
    async def callback(self, interaction: discord.Interaction):
        try:
            message = await self.channel.fetch_message(int(self.message_id.value))
            await message.edit(self.message_content.value)
            await interaction.send("Message edited!", ephemeral = True)
        except:
            await interaction.send("Message ID has to be an integer and has to be in the channel chosen!", ephemeral = True)

@bot.slash_command(name = "edit_message", description = "Edit message using the bot (for mods)")
async def edit_message(interaction: discord.Interaction, channel: discord.abc.GuildChannel = discord.SlashOption(name = "channel", description = "The channel where the message is located", required = True)):
    if not await is_moderator(interaction.user):
        await interaction.send("You are not authorized to perform this action.", ephemeral = True)
        return
    await interaction.response.send_modal(modal = EditMessage(channel))

@bot.command(description="Edit messages using the bot (for mods)")
async def edit_message(ctx,
                       new_message_text: str,
                       message_to_edit: discord.Message):
    if not await is_moderator(ctx.author):
        await ctx.send("You are not authorized to perform this action.")
        return
    if message_to_edit:
        await message_to_edit.edit(content=new_message_text)
        await ctx.send("Done!")
    else:
        await ctx.send("Please add the link to the message to edit at the end of your command!")

@bot.slash_command(description="Suggest an emote for the server!")
async def submit_emote(interaction: discord.Interaction,
                       name: str = discord.SlashOption(name="name", description="Name for emote", required=True),
                       img: discord.Attachment = discord.SlashOption(name="image",
                                                                     description="Image to create emote from",
                                                                     required=True)):
    if "image" in img.content_type:
        await interaction.response.defer(ephemeral=True)
        channel_id = gpdb.get_pref('emote_channel', interaction.guild.id)

        if channel_id:
            channel = interaction.guild.get_channel(channel_id)
            if " " in name:
                await interaction.send("Spaces are not allowed in emoji names!", ephemeral=True)
                return
            if not (name[0] == ":" and name[-1] == ":"):
                name = f":{name}:"
            msg = await channel.send(
                f"New emote suggestion by {interaction.user.mention} `{name}`",
                file=await img.to_file())
            await msg.add_reaction("👍")
            await msg.add_reaction("🔒")
            await msg.add_reaction("👎")
            await interaction.send("Done!", ephemeral=True)
        else:
            await interaction.send(
                "Emote voting is not set up on this server. Please ask a moderator/admin to set it up using `/set_preferences`!",
                ephemeral=True)
    else:
        await interaction.send("Invalid input!", ephemeral=True)


@bot.slash_command(description="Pong!")
async def ping(interaction: discord.Interaction):
    await interaction.send("Pong!")


@bot.slash_command(description="Get a random joke")
async def joke(interaction: discord.Interaction):
    await interaction.response.defer()
    req = requests.get("https://icanhazdadjoke.com/", headers={"Accept": "application/json"})
    jsonobj = req.json()
    joke = jsonobj['joke']
    await interaction.send(joke)


# Resources Command


class Groups(discord.ui.Select):
    def __init__(self):
        options = []
        for group in subreddits.keys():
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
        for subject in subreddits[group].keys():
            view.add_item(
                discord.ui.Button(label=subject, style=discord.ButtonStyle.url, url=subreddits[group][subject]))
        await interaction.response.edit_message(view=view)


class DropdownView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Groups())


@bot.slash_command(description="View the r/igcse resources repository", guild_ids=[GUILD_ID])
async def resources(interaction: discord.Interaction):
    await interaction.send(view=DropdownView())


# Search past papers

@bot.slash_command(description="Search for IGCSE past papers with subject code/question text")
async def search(interaction: discord.Interaction,
                 query: str = discord.SlashOption(name="query", description="Search query", required=True)):
    await interaction.response.defer(ephemeral=True)
    try:
        response = requests.get(f"https://paper.sc/search/?as=json&query={query}").json()
        if len(response['list']) == 0:
            await interaction.send("No results found in past papers. Try changing your query for better results.",
                                   ephemeral=True)
        else:
            embed = discord.Embed(title="Potential Match",
                                  description="Your question matched a past paper question!",
                                  colour=discord.Colour.green())
            for n, item in enumerate(response['list'][:3]):
                # embed.add_field(name="Result No.", value=str(n+1), inline=False)
                embed.add_field(name="Subject", value=item['doc']['subject'], inline=True)
                embed.add_field(name="Paper", value=item['doc']['paper'], inline=True)
                embed.add_field(name="Session", value=item['doc']['time'], inline=True)
                embed.add_field(name="Variant", value=item['doc']['variant'], inline=True)
                embed.add_field(name="QP Link", value=f"https://paper.sc/doc/{item['doc']['_id']}", inline=True)
                embed.add_field(name="MS Link", value=f"https://paper.sc/doc/{item['related'][0]['_id']}",
                                inline=True)
            await interaction.send(embed=embed, ephemeral=True)
    except:
        await interaction.send("No results found in past papers. Try changing your query for better results.",
                               ephemeral=True)


@bot.slash_command(description="Set server preferences (for mods)")
async def set_preferences(interaction: discord.Interaction,
                          modlog_channel: discord.abc.GuildChannel = discord.SlashOption(name="modlog_channel",
                                                                                         description="Channel for log of timeouts, bans, etc.",
                                                                                         required=False),
                          rep_enabled: bool = discord.SlashOption(name="rep_enabled",
                                                                  description="Enable the reputation system?",
                                                                  required=False),
                          suggestions_channel: discord.abc.GuildChannel = discord.SlashOption(
                              name="suggestions_channel",
                              description="Channel for new server suggestions to be displayed and voted upon.",
                              required=False),
                          warnlog_channel: discord.abc.GuildChannel = discord.SlashOption(
                              name="warnlog_channel",
                              description="Channel for warns to be logged.",
                              required=False),
                          emote_channel: discord.abc.GuildChannel = discord.SlashOption(
                              name="emote_channel",
                              description="Channel for emote voting to take place.",
                              required=False)):
    if not await is_moderator(interaction.user):
        await interaction.send("You are not authorized to perform this action", ephemeral=True)
        return
    await interaction.response.defer()
    if modlog_channel:
        gpdb.set_pref('modlog_channel', modlog_channel.id, interaction.guild.id)
    if rep_enabled:
        gpdb.set_pref('rep_enabled', rep_enabled, interaction.guild.id)
    if suggestions_channel:
        gpdb.set_pref("suggestions_channel", suggestions_channel.id, interaction.guild.id)
    if warnlog_channel:
        gpdb.set_pref("warnlog_channel", warnlog_channel.id, interaction.guild.id)
    if emote_channel:
        gpdb.set_pref("emote_channel", emote_channel.id, interaction.guild.id)
    await interaction.send("Done.")


@bot.slash_command(description="Check a user's previous offenses (warns/timeouts/bans)")
async def history(interaction: discord.Interaction, user: discord.User = discord.SlashOption(name="user", description="User to view history of", required=True)):
    if not await is_moderator(interaction.user) and not await has_role(interaction.user, "Chat Moderator"):
        await interaction.send("You are not permitted to use this command.", ephemeral=True)
    await interaction.response.defer()
    modlog = gpdb.get_pref("modlog_channel", interaction.guild.id)
    warnlog = gpdb.get_pref("warnlog_channel", interaction.guild.id)
    if modlog and warnlog:
        history = []
        modlog = bot.get_channel(modlog)
        warnlog = bot.get_channel(warnlog)
        warn_history = await warnlog.history(limit=750).flatten()
        modlog_history = await modlog.history(limit=500).flatten()
        for msg in warn_history:
            if str(user.id) in msg.content:
                history.append(msg.clean_content)
        for msg in modlog_history:
            if str(user.id) in msg.content:
                history.append(msg.clean_content)
        if len(history) == 0:
            await interaction.send(f"{user} does not have any previous offenses.", ephemeral=False)
        else:
            text = ('\n\n'.join(history))[:1900]
            await interaction.send(f"{user}'s Moderation History:\n```{text}```", ephemeral=False)
    else:
        await interaction.send("Please set up your moglog and warnlog through /set_preferences first!")


@bot.slash_command(description="Warn a user (for mods)")
async def warn(interaction: discord.Interaction, user: discord.Member = discord.SlashOption(name="user", description="User to warn", required=True), reason: str = discord.SlashOption(name="reason", description="Reason for warn", required=True)):
    action_type = "Warn"
    mod = interaction.user
    if await is_banned(user, interaction.guild):
        await interaction.send("User is banned from the server!", ephemeral=True)
        return
    if await is_moderator(user) or (not await is_moderator(interaction.user) and not await has_role(interaction.user, "Chat Moderator")):
        await interaction.send(f"Sorry {mod}, you don't have the permission to perform this action.", ephemeral=True)
        return
    await interaction.response.defer()
    warnlog_channel = gpdb.get_pref("warnlog_channel", interaction.guild.id)
    if warnlog_channel:
        ban_msg_channel = bot.get_channel(warnlog_channel)
        try:
            last_ban_msg = await ban_msg_channel.history(limit=1).flatten()
            case_no = int(''.join(list(filter(str.isdigit, last_ban_msg[0].content.splitlines()[0])))) + 1
        except:
            case_no = 1
        ban_msg = f"""Case #{case_no} | [{action_type}]
Username: {str(user)} ({user.id})
Moderator: {mod} 
Reason: {reason}"""
        await interaction.send(f"{str(user)} has been warned.")
        await ban_msg_channel.send(ban_msg)
    channel = await user.create_dm()
    await channel.send(
        f"You have been warned in r/IGCSE by moderator {mod} for \"{reason}\".\n\nPlease be mindful in your further interaction in the server to avoid further action being taken against you, such as a timeout or a ban.")

@bot.slash_command(description="Make an anonymous confession.")
async def confess(interaction: discord.Interaction,
                  confession: str =
                    discord.SlashOption(name="confession",
                                        description="Write your confession and it will be sent anonymously", required=True)):
    if interaction.guild.id != GUILD_ID:
        await interaction.send("This command is not available on this server.")
        return
    
    mods_channel = interaction.guild.get_channel(984718514579464224)
    confession_channel = interaction.guild.get_channel(965177290814267462)

    view = discord.ui.View(timeout=None)
    approveBTN = discord.ui.Button(label="Approve", style=discord.ButtonStyle.blurple)
    rejectBTN = discord.ui.Button(label="Reject", style=discord.ButtonStyle.red)

    async def ApproveCallBack(interaction):
        embed = discord.Embed(colour=discord.Colour.green(), description=confession)
        embed.set_author(name=f"Approved by {interaction.user}", icon_url=interaction.user.display_avatar.url)
        await interaction.edit(embed=embed, view=None)
        embed = discord.Embed(colour=discord.Colour.random(), description=confession)
        await confession_channel.send(content="New Anonymous Confession", embed=embed)
#         await anon_approve_mgs.delete()
    approveBTN.callback = ApproveCallBack

    async def RejectCallBack(interaction):
        embed = discord.Embed(colour=discord.Colour.red(), description=confession)
        embed.set_author(name=f"Rejected by {interaction.user}", icon_url=interaction.user.display_avatar.url)
        await interaction.edit(embed=embed, view=None)
#         await anon_approve_mgs.delete()
    rejectBTN.callback = RejectCallBack

    view.add_item(approveBTN)
    view.add_item(rejectBTN)
    embed = discord.Embed(colour=discord.Colour.random(), description=confession)
    anon_approve_mgs = await mods_channel.send(embed=embed, view=view)
    await interaction.send("Your confession has been sent to the moderators.\nYou have to wait for their approval.", ephemeral=True)

@bot.slash_command(description="Timeout a user (for mods)")
async def timeout(interaction: discord.Interaction,
                  user: discord.Member = discord.SlashOption(name="user", description="User to timeout",
                                                             required=True),
                  time_: str = discord.SlashOption(name="duration",
                                                   description="Duration of timeout (e.g. 1d5h) up to 28 days (use 'permanent')",
                                                   required=True),
                  reason: str = discord.SlashOption(name="reason", description="Reason for timeout", required=True)):
    action_type = "Timeout"
    mod = interaction.user.mention
    if await is_banned(user, interaction.guild):
        await interaction.send("User is banned from the server!", ephemeral=True)
        return
    if await is_moderator(user) or (not await is_moderator(interaction.user) and not await has_role(interaction.user, "Chat Moderator")):
        await interaction.send(f"Sorry {mod}, you don't have the permission to perform this action.", ephemeral=True)
        return
    await interaction.response.defer()
    if time_.lower() == "unspecified" or time_.lower() == "permanent" or time_.lower() == "undecided":
        seconds = 86400 * 28
    else:
        seconds = 0
        if "d" in time_:
            seconds += int(time_.split("d")[0]) * 86400
            time_ = time_.split("d")[1]
        if "h" in time_:
            seconds += int(time_.split("h")[0]) * 3600
            time_ = time_.split("h")[1]
        if "m" in time_:
            seconds += int(time_.split("m")[0]) * 60
            time_ = time_.split("m")[1]
        if "s" in time_:
            seconds += int(time_.split("s")[0])
    if seconds == 0:
        await interaction.send("You can't timeout for zero seconds!", ephemeral=True)
        return
    await user.edit(timeout=discord.utils.utcnow() + datetime.timedelta(seconds=seconds))
    human_readable_time = f"{seconds // 86400}d {(seconds % 86400) // 3600}h {(seconds % 3600) // 60}m {seconds % 60}s"
    ban_msg_channel = bot.get_channel(gpdb.get_pref("modlog_channel", interaction.guild.id))
    if ban_msg_channel:
        try:
            last_ban_msg = await ban_msg_channel.history(limit=1).flatten()
            case_no = int(''.join(list(filter(str.isdigit, last_ban_msg[0].content.splitlines()[0])))) + 1
        except:
            case_no = 1
        ban_msg = f"""Case #{case_no} | [{action_type}]
Username: {str(user)} ({user.id})
Moderator: {mod} 
Reason: {reason}
Duration: {human_readable_time}
Until: <t:{int(time.time()) + seconds}> (<t:{int(time.time()) + seconds}:R>)"""
        await ban_msg_channel.send(ban_msg)
    await user.send(f'''You have been given a timeout on the r/IGCSE server 
Reason: {reason}
Duration: {human_readable_time}
Until: <t:{int(time.time()) + seconds}> (<t:{int(time.time()) + seconds}:R>)''')
    await interaction.send(
        f"{str(user)} has been put on time out until <t:{int(time.time()) + seconds}>, which is <t:{int(time.time()) + seconds}:R>.")


@bot.slash_command(description="Untimeout a user (for mods)")
async def untimeout(interaction: discord.Interaction,
                    user: discord.Member = discord.SlashOption(name="user", description="User to untimeout",
                                                               required=True)):
    action_type = "Remove Timeout"
    mod = interaction.user.mention
    if await is_banned(user, interaction.guild):
        await interaction.send("User is banned from the server!", ephemeral=True)
        return
    if await is_moderator(user) or (not await is_moderator(interaction.user) and not await has_role(interaction.user, "Chat Moderator")):
        await interaction.send(f"Sorry {mod}, you don't have the permission to perform this action.", ephemeral=True)
        return
    await interaction.response.defer()
    await user.edit(timeout=None)
    ban_msg_channel = bot.get_channel(gpdb.get_pref("modlog_channel", interaction.guild.id))
    if ban_msg_channel:
        try:
            last_ban_msg = await ban_msg_channel.history(limit=1).flatten()
            case_no = int(''.join(list(filter(str.isdigit, last_ban_msg[0].content.splitlines()[0])))) + 1
        except:
            case_no = 1
        ban_msg = f"""Case #{case_no} | [{action_type}]
Username: {str(user)} ({user.id})
Moderator: {mod}"""
        await ban_msg_channel.send(ban_msg)
    await interaction.send(f"Timeout has been removed from {str(user)}.")


@bot.slash_command(description="Ban a user from the server (for mods)")
async def ban(
        interaction: discord.Interaction,
        user: discord.Member = discord.SlashOption(name="user", description="User to ban", required=True),
        reason: str = discord.SlashOption(name="reason", description="Reason for ban", required=True),
        delete_message_days: int = discord.SlashOption(name="delete_messages", choices={"Don't Delete Messages" : 0, "Delete Today's Messages" : 1, "Delete 3 Days of Messages" : 3, 'Delete 1 Week of Messages' : 7}, default=0, description="Duration of messages from the user to delete (defaults to zero)", required=False)
    ):
    action_type = "Ban"
    mod = interaction.user.mention

    if type(user) is not discord.Member:
        await interaction.send("User is not a member of the server", ephemeral=True)
        return 
    if await is_moderator(user) or not await is_moderator(interaction.user) or await has_role(interaction.user, "Temp Mod"):
        await interaction.send(f"Sorry {mod}, you don't have the permission to perform this action.", ephemeral=True)
        return
    if await is_banned(user, interaction.guild):
        await interaction.send("User is banned from the server!", ephemeral=True)
        return
    await interaction.response.defer()
    try:
        if interaction.guild.id == GUILD_ID:  # r/igcse
            await user.send(
                f"Hi there from {interaction.guild.name}. You have been banned from the server due to '{reason}'. If you feel this ban was done in error, to appeal your ban, please fill the form below.\nhttps://forms.gle/8qnWpSFbLDLdntdt8")
        else:
            await user.send(
                f"Hi there from {interaction.guild.name}. You have been banned from the server due to '{reason}'.")
    except:
        pass
    ban_msg_channel = bot.get_channel(gpdb.get_pref("modlog_channel", interaction.guild.id))
    if ban_msg_channel:
        try:
            last_ban_msg = await ban_msg_channel.history(limit=1).flatten()
            case_no = int(''.join(list(filter(str.isdigit, last_ban_msg[0].content.splitlines()[0])))) + 1
        except:
            case_no = 1
        ban_msg = f"""Case #{case_no} | [{action_type}]
Username: {str(user)} ({user.id})
Moderator: {mod} 
Reason: {reason}"""
        await ban_msg_channel.send(ban_msg)
    await interaction.guild.ban(user, delete_message_days=delete_message_days)
    await interaction.send(f"{str(user)} has been banned.")


@bot.slash_command(description="Unban a user from the server (for mods)")
async def unban(interaction: discord.Interaction, user: discord.User = discord.SlashOption(name="user", description="User to unban", required=True)):
    action_type = "Unban"
    mod = interaction.user.mention
    if not await is_moderator(interaction.user):
        await interaction.send(f"Sorry {mod}, you don't have the permission to perform this action.", ephemeral=True)
        return
    await interaction.response.defer()
    await interaction.guild.unban(user)
    await interaction.send(f"{str(user)} has been unbanned.")

    ban_msg_channel = bot.get_channel(gpdb.get_pref("modlog_channel", interaction.guild.id))
    if ban_msg_channel:
        try:
            last_ban_msg = await ban_msg_channel.history(limit=1).flatten()
            case_no = int(''.join(list(filter(str.isdigit, last_ban_msg[0].content.splitlines()[0])))) + 1
        except:
            case_no = 1
        ban_msg = f"""Case #{case_no} | [{action_type}]
Username: {str(user)} ({user.id})
Moderator: {mod}"""
        await ban_msg_channel.send(ban_msg)


@bot.slash_command(description="Kick a user from the server (for mods)")
async def kick(interaction: discord.Interaction,
               user: discord.Member = discord.SlashOption(name="user", description="User to kick",
                                                        required=True),
               reason: str = discord.SlashOption(name="reason", description="Reason for kick", required=True)):
    action_type = "Kick"
    mod = interaction.user.mention
    if await is_moderator(user) or not await is_moderator(interaction.user):
        await interaction.send(f"Sorry {mod}, you don't have the permission to perform this action.", ephemeral=True)
        return
    if await is_banned(user, interaction.guild):
        await interaction.send("User is banned from the server!", ephemeral=True)
        return
    await interaction.response.defer()
    try:
        await user.send(
            f"Hi there from {interaction.guild.name}. You have been kicked from the server due to '{reason}'.")
    except:
        pass
    ban_msg_channel = bot.get_channel(gpdb.get_pref("modlog_channel", interaction.guild.id))
    if ban_msg_channel:
        try:
            last_ban_msg = await ban_msg_channel.history(limit=1).flatten()
            case_no = int(''.join(list(filter(str.isdigit, last_ban_msg[0].content.splitlines()[0])))) + 1
        except:
            case_no = 1
        ban_msg = f"""Case #{case_no} | [{action_type}]
Username: {str(user)} ({user.id})
Moderator: {mod} 
Reason: {reason}"""
        await ban_msg_channel.send(ban_msg)
    await interaction.guild.kick(user)
    await interaction.send(f"{str(user)} has been kicked.")


# Study Sessions




@bot.slash_command(description="Start a study session", guild_ids=[GUILD_ID])
async def study_session(interaction: discord.Interaction):
    try:
        role = interaction.guild.get_role(study_roles[interaction.channel.id])
    except:
        await interaction.send(
            "Please use this command in the subject channel of the subject you're starting a study session for.",
            ephemeral=True)
        return
    await interaction.response.defer()
    study_sesh_channel = bot.get_channel(941276796937179157)
    msg_history = await study_sesh_channel.history(limit=3).flatten()
    for msg in msg_history:
        if (str(interaction.user.mention) in msg.content or str(role.mention) in msg.content) and \
                (msg.created_at.replace(tzinfo=None) + datetime.timedelta(minutes=60) > datetime.datetime.utcnow()):
            await interaction.send(
                "Please wait until one hour after your previous ping or after a study session in the same subject to start a new study session.",
                ephemeral=True)
            return
    voice_channel = interaction.user.voice
    if voice_channel is None:
        await interaction.send("You must be in a voice channel to use this command.", ephemeral=True)
    else:
        await study_sesh_channel.send(
            f"{role.mention} - Requested by {interaction.user.mention} - Please join {voice_channel.channel.mention}")
        await interaction.send(
            f"Started a {role.name.lower().replace(' study ping', '').title()} study session at {voice_channel.channel.mention}.")
        await voice_channel.channel.edit(
            name=f"{role.name.lower().replace(' study ping', '').title()} Study Session")

        
# Helper of the month voting system

@bot.slash_command(description="Vote for the helper of the month", guild_ids=[GUILD_ID])
async def votehotm(interaction: discord.Interaction,
                    helper: discord.Member =
                    discord.SlashOption(name="helper",
                                        description="Choose the helper to vote for", required=True)):
    if helper.bot:
        await interaction.send("You can't vote for a bot.", ephemeral=True)
    elif await is_helper(helper):
        await interaction.response.defer(ephemeral=True)
        client = pymongo.MongoClient(LINK)
        db = client.IGCSEBot
        helpers = db.hotmhelpers
        voters = db.hotmvoters

        voter = voters.find_one({"id": interaction.user.id})
        if not voter:
            # Insert decreased votes_left into database
            voter = {"id": interaction.user.id,
                     "votes_left": 2}
            voters.insert_one(voter)
        else:
            if voter['votes_left'] == 0:
                await interaction.send("You can't vote more than 3 times.", ephemeral=True)
                return
            
            # Decrease votes by one
            voters.update_one({'id': interaction.user.id}, {"$inc": {"votes_left": -1}})
            voter['votes_left'] = voter['votes_left'] - 1
        
        await interaction.send(f"Done! You have {int(voter['votes_left'])} votes left.", ephemeral=True)
            
        helpers.update_one({"id": helper.id}, {"$inc": {"votes": 1}}, upsert=True)  # Update vote count for helpers    
        
        # Update results message
        messages = [msg for msg in await bot.get_channel(991202262472998962).history().flatten() if
                    msg.author.id == 861445044790886467 and msg.content == "HOTM Voting Results"] 
        if len(messages) == 0:
            results_message = await bot.get_channel(991202262472998962).send(content="HOTM Voting Results")
        else:
            results_message = messages[0]

        embed = discord.Embed(colour=5111808, description="**Results:**")

        sorted_helpers = helpers.find().sort('votes', -1).limit(10)
        for helper in list(sorted_helpers):
            user_name = interaction.guild.get_member(helper['id']).name
            embed.add_field(name=f"**{user_name}**", value=f"Votes: {helper['votes']}", inline=False)
        await results_message.edit(embed=embed)
    else:
        await interaction.send(f"{helper} is not a helper.", ephemeral=True)

@bot.slash_command(name = "resethotm", description = "Reset the Helper of the Month data", guild_ids = [GUILD_ID])
async def resethotm(interaction: discord.Interaction):
    if not await is_moderator(interaction.user):
        await interaction.send("You do not have the necessary permissions to perform this action", ephemeral = True)
        return
    await interaction.response.defer(ephemeral = True)
    client = pymongo.MongoClient(LINK)
    db = client.IGCSEBot
    db.drop_collection("hotmhelpers")
    db.drop_collection("hotmvoters")
    msgs = [msg for msg in await bot.get_channel(991202262472998962).history().flatten() if
                    msg.author.id == 861445044790886467 and msg.content == "HOTM Voting Results"] 
    await msgs[0].delete()
    await interaction.send("Helper of the Month data has been reset!")

# Embeds sending and editing

class NewEmbed(discord.ui.Modal):
    def __init__(self, embed: discord.Embed, embed_msg: discord.Message = None, content: str = None, channel: discord.TextChannel = None):
        self.embed = embed
        self.msg = embed_msg
        self.content = content
        self.channel = channel

        super().__init__("New embed!", timeout = None)

        self.name = discord.ui.TextInput(
            label="Title of the embed",
            style = discord.TextInputStyle.short,
            placeholder = "This will be the title of the embed",
            required = True
        )
        self.add_item(self.name)

        self.description = discord.ui.TextInput(
            label = "Description of the embed",
            style = discord.TextInputStyle.paragraph,
            placeholder = "This will be the description of the embed",
            required = True
        )
        self.add_item(self.description)
    
    async def callback(self, interaction: discord.Interaction) -> None:
        self.embed.title = self.name.value
        self.embed.description = self.description.value
        if self.msg:
            await self.msg.edit(content = self.content, embed = self.embed)
        else:
            await self.channel.send(content = self.content, embed = self.embed)
        await interaction.send("Done!",ephemeral=True, delete_after=1)

@bot.slash_command(description="send and edit embeds (for mods)")
async def embed(interaction: discord.Interaction,
                channel: discord.abc.GuildChannel = discord.SlashOption(name="channel", description="Default is the channel you use the command in", channel_types = [discord.ChannelType.text], required=False),
                content: str = discord.SlashOption(name="content", description="The content of the embed", required=False),
                colour: str = discord.SlashOption(name="colour", description="The hexadecimal colour code for the embed (Default is green)", required=False),
                message_id: str=discord.SlashOption(name='message_id', description='The id of the message embed you want to edit', required=False)):
    if not await is_moderator(interaction.user):
        await interaction.send("You do not have the necessary permissions to perform this action", ephemeral = True)
        return
    if channel:
        embed_channel = channel
    else:
        embed_channel = interaction.channel
    if message_id:
        embed_message = await embed_channel.fetch_message(int(message_id))
        previous_embed = embed_message.embeds[0]
        embed = discord.Embed(colour=previous_embed.colour, title=previous_embed.title, description=previous_embed.description)
    else:
        embed = discord.Embed()
        embed_message = None
    if colour:
        try:
            embed.colour = int(colour[1:], 16)
        except:
            await interaction.send('Invalid Hex code', ephemeral=True)
            return
    else:
        embed.colour = discord.Colour.green()
    modal = NewEmbed(embed, embed_message, content, embed_channel)
    await interaction.response.send_modal(modal)

@bot.slash_command(name = "poll")
async def poll(interaction: discord.Interaction):
    pass

class Poll(discord.ui.Modal):
    def __init__(self, options: list, channel: discord.TextChannel):
        self.options = options
        self.channel = channel

        super().__init__("New poll!", timeout = None)

        self.name = discord.ui.TextInput(
            label = "Title of the message",
            style = discord.TextInputStyle.short,
            placeholder = "This will be the title of the poll",
            required = True
        )
        self.add_item(self.name)

        self.description = discord.ui.TextInput(
            label = "Content of the message",
            style = discord.TextInputStyle.paragraph,
            placeholder = "This will be the message in the poll",
            required = False
        )
        self.add_item(self.description)

    async def callback(self, interaction: discord.Interaction):
        poll_embed = discord.Embed(title = self.name.value, description = self.description.value, colour = discord.Colour.orange())
        options_field = ""
        emojis = []
        for x in range(1, len(self.options)+1):
            if x == 1:
                emoji = "1️⃣"
            elif x == 2:
                emoji = "2️⃣"
            elif x == 3:
                emoji = "3️⃣"
            elif x == 4:
                emoji = "4️⃣"
            elif x == 5:
                emoji = "5️⃣"
            elif x == 6:
                emoji = "6️⃣"
            elif x == 7:
                emoji = "7️⃣"
            elif x == 8:
                emoji = "8️⃣"
            elif x == 9:
                emoji = "9️⃣"
            else:
                emoji = "🔟"
            
            emojis.append(emoji)
            options_field += emoji + " " + self.options[x-1] + "\n"
        
        poll_embed.add_field(name = "Options", value = options_field)

        poll_msg = await self.channel.send(embed = poll_embed)
        for emoji in emojis:
            await poll_msg.add_reaction(emoji)
        await interaction.send("Poll created!", ephemeral = True)

@poll.subcommand(name = "create", description = "Create a new poll")
async def create(interaction: discord.Interaction, option_1: str = discord.SlashOption(name = "option-1", description = "Option 1", required = True), option_2: str = discord.SlashOption(name = "option-2", description = "Option 2", required = False), option_3: str = discord.SlashOption(name = "option-3", description = "Option 3", required = False), option_4: str = discord.SlashOption(name = "option-4", description = "Option 4", required = False), option_5: str = discord.SlashOption(name = "option-5", description = "Option 5", required = False), option_6: str = discord.SlashOption(name = "option-6", description = "Option 6", required = False), option_7: str = discord.SlashOption(name = "option-7", description = "Option 7", required = False), option_8: str = discord.SlashOption(name = "option-8", description = "Option 8", required = False), option_9: str = discord.SlashOption(name = "option-9", description = "Option 9", required = False), option_10: str = discord.SlashOption(name = "option-10", description = "Option 10", required = False)):
    if not await is_moderator(interaction.user):
        await interaction.send("You do not have the required permissions to use this command!", ephemeral = True)
        return
    options = [option_1, option_2, option_3, option_4, option_5, option_6, option_7, option_8, option_9, option_10]
    while True:
        try:
            options.remove(None)
        except ValueError:
            break
    modal = Poll(options, interaction.channel)
    await interaction.response.send_modal(modal)

@poll.subcommand(name = "results", description = "Get the results for a poll")
async def results(interaction: discord.Interaction, link: str = discord.SlashOption(name = "link", description = "The link of the message with the poll", required = True)):
    try:
        msg_id = int(link.split("/")[-1])
        msg = await interaction.channel.fetch_message(msg_id)
        if msg.author != bot.user:
            await interaction.send("This message was not sent by the bot!", ephemeral = True)
            return
    except:
        await interaction.send("Invalid message link!", ephemeral = True)
        return
    
    reactions_list = msg.reactions
    reactions = {}
    embed = msg.embeds[0]
    options = embed.fields[0].value.split("\n")
    for x in range(1, len(options)+1):
        if x == 1:
            emoji = "1️⃣"
        elif x == 2:
            emoji = "2️⃣"
        elif x == 3:
            emoji = "3️⃣"
        elif x == 4:
            emoji = "4️⃣"
        elif x == 5:
            emoji = "5️⃣"
        elif x == 6:
            emoji = "6️⃣"
        elif x == 7:
            emoji = "7️⃣"
        elif x == 8:
            emoji = "8️⃣"
        elif x == 9:
            emoji = "9️⃣"
        else:
            emoji = "🔟"
        count = discord.utils.get(reactions_list, emoji = emoji)
        reactions[emoji] = count.count-1
    total = sum(list(reactions.values()))
    results_embed = discord.Embed(title = embed.title, colour = discord.Colour.orange())

    for x in range(1, len(options)+1):
        if x == 1:
            emoji = "1️⃣"
        elif x == 2:
            emoji = "2️⃣"
        elif x == 3:
            emoji = "3️⃣"
        elif x == 4:
            emoji = "4️⃣"
        elif x == 5:
            emoji = "5️⃣"
        elif x == 6:
            emoji = "6️⃣"
        elif x == 7:
            emoji = "7️⃣"
        elif x == 8:
            emoji = "8️⃣"
        elif x == 9:
            emoji = "9️⃣"
        else:
            emoji = "🔟"
        colours = "🟩"*(reactions[emoji]*10//total)+"🟥"*(10-(reactions[emoji]*10//total))
        results_embed.add_field(name = options[x-1], value = colours+f"{reactions[emoji]*100//total}%", inline = False)
    
    await interaction.send(embed = results_embed)

class Feedback(discord.ui.Modal):
    def __init__(self):
        super().__init__("Feedback!", timeout = None)

        self.feedback = discord.ui.TextInput(
            label = "Your feedback",
            style = discord.TextInputStyle.paragraph,
            placeholder = "The message you would like to send as feedback",
            required = True
        )
        self.add_item(self.feedback)
    
    async def callback(self, interaction: discord.Interaction):
        feedback_channel = await bot.fetch_channel(1057505291014524939)
        feedback_embed = discord.Embed(title = "Feedback Received", colour = discord.Colour.blue())
        feedback_embed.set_author(name=str(interaction.user), icon_url=interaction.user.display_avatar.url)
        feedback_embed.add_field(name = "Message", value = self.feedback.value)
        await feedback_channel.send(embed = feedback_embed)
        await interaction.send("Feedback sent!", ephemeral = True)

@bot.slash_command(name = "feedback", description = "Submit some feedback to the mods!")
async def feedback(interaction: discord.Interaction):
    await interaction.response.send_modal(modal = Feedback())

class ChatModerator(discord.ui.Modal):
    def __init__(self):
        super().__init__("Chat Moderator Application", timeout = None)

        self.timezone = discord.ui.TextInput(
            label = "Timezone",
            style = discord.TextInputStyle.short,
            placeholder = "Please specify your timezone in UTC/GMT time",
            required = True
        )
        self.add_item(self.timezone)
    
    async def callback(self, interaction: discord.Interaction):
        channel = bot.get_channel(1070571771423621191)

        application_embed = discord.Embed(title = "New application received", colour = discord.Colour.blue())
        application_embed.add_field(name = "User", value = interaction.user)
        application_embed.add_field(name = "Position", value = "Chat Moderator")
        application_embed.add_field(name = "Timezone", value = self.timezone.value)

        await channel.send(embed = application_embed)
        await interaction.send("Thank you for applying. If you are selected as a Chat Moderator, we will send you a modmail with more information. Good luck!", ephemeral = True)

class ApplyDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label = "Chat Moderator", description = "Apply for the chat moderator position", emoji = "💬")
        ]
        super().__init__(placeholder = "Select the application type", min_values = 1, max_values = 1, options = options)
    
    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "Chat Moderator":
            chat_modal = ChatModerator()
            await interaction.response.send_modal(modal = chat_modal)

@bot.slash_command(name = "apply", description = "Apply for positions in the Discord server")
async def apply(interaction: discord.Interaction):
    view = discord.ui.View()
    view.add_item(ApplyDropdown())
    await interaction.send(view = view, ephemeral = True)


def display_data(data):
    output = ""
    for item in data:
        if isinstance(item, list):
            output += display_data(item)
        else:
            output += item + "\n"
    return output

class Code(discord.ui.Modal):
    def __init__(self):
        super().__init__("Code", timeout = None)

        self.code = discord.ui.TextInput(
            label = "Code",
            style = discord.TextInputStyle.paragraph,
            placeholder = "The code you would like to compile/test",
            required = True
        )
        self.add_item(self.code)
    
    async def callback(self, interaction: discord.Interaction):
        response = requests.post("https://fourth-fresh-boater.glitch.me/apiv1/", data=json.dumps({"code" : str(self.code.value)}))
        if response.status_code == 201:
            finalOutput = display_data(response.json())
            embed = discord.Embed(title = "Code compiled!", colour = discord.Colour.green())
            value = f'''```
{self.code.value}```
            
            **Output**
            ```
{finalOutput}```'''
            embed.add_field(name = "Code", value = value)
            await interaction.send(embed = embed, ephemeral = False)
        else:
            await interaction.send("There was an error compiling the code", ephemeral = True)
            
@bot.slash_command(name = "code", description = "Compile a pseudocode code and send it back")
async def code(interaction: discord.Interaction):
    await interaction.response.send_modal(modal = Code())

@bot.slash_command(description= "gets the current unix timestamp.")
async def unixtime(interaction: discord.Interaction):
    timern = int(time.time()) + 1
    await interaction.send(f"Current time in unix format: `{timern}`")

@bot.slash_command(name="channellock", description="Locks a channel at a specified time")
async def channellockcommand(interaction: discord.Interaction,
                        channelinput: discord.TextChannel =  discord.SlashOption(name="channel_name", description="Which channel do you want to lock?", required=True),
                        locktime: str = discord.SlashOption(name="lock_time", description="At what time do you want the channel to be locked?", required=True),
                        unlocktime: str = discord.SlashOption(name="unlock_time", description="At what time do you want the channel to be unlocked?", required=True)):

        #check if user is moderator or check if "Bot Developer" role is avaliable:
        await interaction.response.defer(ephemeral=True)
        if not await is_moderator(interaction.user) and not await has_role(interaction.user, "Bot Developer"):
                await interaction.send(f"Sorry {interaction.user.mention}," " you don't have the permission to perform this action.", ephemeral=True)
                return
        
        #effectively resets channellock database. for developer purposes
        if locktime == "resolveall" and unlocktime == "!@#$%^&*()":
            client = pymongo.MongoClient(LINK)
            db = client.IGCSEBot
            locks = db["channellock"]
            results = locks.find({"resolved": False})
            for result in results:
                locks.update_one({"_id": result["_id"]}, {"$set": {"resolved": True}})

        #Validate Time:
        t = int(time.time()) + 1
        try:
            locktime = max(int(locktime), t)
            unlocktime = max(int(unlocktime), t)
        except ValueError:
            await interaction.send(f"Sorry {interaction.user.mention}," " values of the time should be positive integers only. please try again.", ephemeral=True)
            return
        
        if locktime > unlocktime:
            await interaction.send("the unlock time has to be after lock time. please try again.", ephemeral=True)
            return
        
        #Getting Valid Unix Timestamp:
        unixlocktime = f"<t:{locktime}:F>"
        unixunlocktime = f"<t:{unlocktime}:F>"
        Channel_ID = f"<#{channelinput.id}>"

        #sending a message in the channel where the command was used in:
        await interaction.send(f"{Channel_ID} is scheduled to lock on {unixlocktime} and unlock on {unixunlocktime}", ephemeral=True)

        #logging a message in #logs:
        User_ID = f"<@{interaction.user.id}>"
        Channel_ID = f"<#{channelinput.id}>"
        Logging = bot.get_channel(MODLOG_CHANNEL_ID)
        await Logging.send(
                            f"Action Type: Channel Lockdown\n"
                            f"Channel Name: {Channel_ID}\n" 
                            f"Lock Time: {locktime} ({unixlocktime})\n" 
                            f"Unlock Time: {unlocktime} ({unixunlocktime})\n" 
                            f"Moderator: {User_ID}"
                            )
        
        client = pymongo.MongoClient(LINK)
        db = client.IGCSEBot
        locks = db["channellock"]

        locks.insert_one({"_id": "l" + str(t), "Channel_ID": channelinput.id,
                        "unlock": False, "time": locktime,
                        "resolved": False})

        locks.insert_one({"_id": "u" + str(t), "Channel_ID": channelinput.id,
                        "unlock": True, "time": unlocktime,
                        "resolved": False})

        await channelinput.send(f"This channel has been scheduled to lock <t:{max(locktime, t)}:R>.")

@bot.slash_command(name="forumlock", description="Locks a forum thread at a specified time")
async def forumlockcommand(interaction: discord.Interaction, threadinput: discord.Thread = discord.SlashOption(name="thread_name", description="Which thread do you want to lock?", required=True), locktime: str = discord.SlashOption(name="lock_time", description="At what time do you want the thread to be locked?", required=True), unlocktime: str = discord.SlashOption(name="unlock_time", description="At what time do you want the thread to be unlocked?", required=True)):
        
        #check if user is moderator or check if "Bot Developer" role is avaliable:
        await interaction.response.defer(ephemeral=True)
        if not await is_moderator(interaction.user) and not await has_role(interaction.user, "Bot Developer"):
                await interaction.send(f"Sorry {interaction.user.mention}," " you don't have the permission to perform this action.", ephemeral=True)
                return
        
        #effectively resets forumlock database. for developer purposes
        if locktime == "resolveall" and unlocktime == "!@#$%^&*()":
            client = pymongo.MongoClient(LINK)
            db = client.IGCSEBot
            locks = db["forumlock"]
            results = locks.find({"resolved": False})
            for result in results:
                locks.update_one({"_id": result["_id"]}, {"$set": {"resolved": True}})

        #Validate Time:
        t = int(time.time()) + 1
        try:
            locktime = max(int(locktime), t)
            unlocktime = max(int(unlocktime), t)
        except ValueError:
                await interaction.send(f"Sorry {interaction.user.mention}," " values of the time should be positive integers only. please try again.", ephemeral=True)
                return
        
        if locktime > unlocktime:
                await interaction.send("the unlock time has to be after lock time. please try again.", ephemeral=True)
                return

        #Getting Valid Unix Timestamp:
        unixlocktime = f"<t:{locktime}:F>"
        unixunlocktime = f"<t:{unlocktime}:F>"
        threadid = f"<#{threadinput.id}>"

        #sending a message in the channel where the command was used in:
        await interaction.send(f"{threadid} is been scheduled to lock on {unixlocktime} and unlock on {unixunlocktime}", ephemeral=True)

        #logging a message in #logs:
        userid = f"<@{interaction.user.id}>"
        logging = bot.get_channel(MODLOG_CHANNEL_ID)
        await logging.send(
                            f"Action Type: Forum Thread Lockdown\n"
                            f"Channel Name: {threadid}\n" 
                            f"Lock Time: {locktime} ({unixlocktime})\n" 
                            f"Unlock Time: {unlocktime} ({unixunlocktime})\n" 
                            f"Moderator: {userid}"
                            )
        
        client = pymongo.MongoClient(LINK)
        db = client.IGCSEBot
        lock = db["forumlock"]

        lock.insert_one({"_id": "l" + str(t), "Thread_ID": threadinput.id,
                        "unlock": False, "time": locktime,
                        "resolved": False})

        lock.insert_one({"_id": "u" + str(t), "Thread_ID": threadinput.id,
                        "unlock": True, "time": unlocktime,
                        "resolved": False})

        await threadinput.send(f"This thread has been scheduled to lock <t:{max(locktime, t)}:R> successfully.")

@bot.slash_command(description="Get a random fun fact")
async def funfact(interaction: discord.Interaction):
    await interaction.response.defer()
    url = "https://uselessfacts.jsph.pl/random.json?language=en"
    response = requests.request("GET", url)
    data = json.loads(response.text)
    useless_fact = data['text']
    await interaction.send(useless_fact)

@bot.slash_command(name="random_pyp", description="gets a random past year paper.")
async def random_pyp(interaction: discord.Interaction, subject_code: str = discord.SlashOption(name="subject_code", description="please enter the subject code", required=True)):
    PAPER_VARIENTS = [1,2,3]
    MARCH_PAPER_VARIENT = 2
    PAPER_YEAR = [2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023]
    SESSION = ['m', 's', 'w']
    validation = IGCSE_SUBJECT_CODES.__contains__(subject_code) or ALEVEL_SUBJECT_CODES.__contains__(subject_code)
    if validation == True:
        sc = subject_code
        s = random.choice(SESSION)
        p = random.choice(PAPER_VARIENTS)
        v = random.choice(PAPER_VARIENTS)
        mv = MARCH_PAPER_VARIENT
        y = random.choice(PAPER_YEAR)
        if s == 'm':
            query = f"{sc}%20qp%20{p}{mv}%20{s}%{y}"
            response = requests.get(f"https://paper.sc/search/?as=json&query={query}").json()
            for n, item in enumerate(response['list'][:1]):
                type = item['doc']['type']
                if "qp" in type:
                    embed = discord.Embed(title="Random Paper Chosen", description=f"`{item['doc']['subject']}_{item['doc']['time']}_qp_{item['doc']['paper']}{item['doc']['variant']}` has been chosen at random. Below are links to the question paper and marking scheme.\n\n**QP LINK**: https://paper.sc/doc/{item['doc']['_id']}\n**MS LINK**: https://paper.sc/doc/{item['related'][0]['_id']}", color=0xf4b6c2)
                    await interaction.send(embed=embed)
                elif "ms" in type:
                    embed = discord.Embed(title="Random Paper Chosen", description=f"`{item['doc']['subject']}_{item['doc']['time']}_qp_{item['doc']['paper']}{item['doc']['variant']}` has been chosen at random. Below are links to the question paper and marking scheme.\n\n**QP LINK**: https://paper.sc/doc/{item['related'][0]['_id']}\n**MS LINK**: https://paper.sc/doc/{item['doc']['_id']}", color=0xf4b6c2)
                    await interaction.send(embed=embed)
                else:
                    await interaction.send("invalid paper is been chosen. please run the command.", ephemeral=True)
        else:
            query = f"{sc}%20qp%20{p}{v}%20{s}%{y}"
            response = requests.get(f"https://paper.sc/search/?as=json&query={query}").json()
            for n, item in enumerate(response['list'][:1]):
                type = item['doc']['type']
                if "qp" in type:
                    embed = discord.Embed(title="Random Paper Chosen", description=f"`{item['doc']['subject']}_{item['doc']['time']}_qp_{item['doc']['paper']}{item['doc']['variant']}` has been chosen at random. Below are links to the question paper and marking scheme.\n\n**QP LINK**: https://paper.sc/doc/{item['doc']['_id']}\n**MS LINK**: https://paper.sc/doc/{item['related'][0]['_id']}", color=0xf4b6c2)
                    await interaction.send(embed=embed)
                elif "ms" in type:
                    embed = discord.Embed(title="Random Paper Chosen", description=f"`{item['doc']['subject']}_{item['doc']['time']}_qp_{item['doc']['paper']}{item['doc']['variant']}` has been chosen at random. Below are links to the question paper and marking scheme.\n\n**QP LINK**: https://paper.sc/doc/{item['related'][0]['_id']}\n**MS LINK**: https://paper.sc/doc/{item['doc']['_id']}", color=0xf4b6c2)
                    await interaction.send(embed=embed)
                else:
                    await interaction.send("invalid paper is been chosen. please run the command.", ephemeral=True)
    else:
        await interaction.send("Please enter a valid subject code for better results.", ephemeral=True)


bot.run(TOKEN)
