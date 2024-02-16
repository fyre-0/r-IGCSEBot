from bot import discord, bot
from utils.constants import GUILD_ID
from utils.mongodb import asmdb


class Stick_Message(discord.ui.Modal):
    def __init__(self, channel_id, stick_time, unstick_time):
        super().__init__("Advstick Message!", timeout=None)
        self.embed_title = discord.ui.TextInput(
            label="Title of the Embed",
            style=discord.TextInputStyle.short,
            placeholder="This will be the title of the embed",
            required=False,
        )
        self.add_item(self.embed_title)

        self.embed_description = discord.ui.TextInput(
            label="Description of the Embed",
            style=discord.TextInputStyle.paragraph,
            placeholder="This will be the description of the embed",
            required=True,
        )
        self.add_item(self.embed_description)

        self.channel_id = channel_id
        self.stick_time = stick_time
        self.unstick_time = unstick_time

    async def callback(self, interaction: discord.Interaction):
        channel_id = self.channel_id
        stick_time = self.stick_time
        unstick_time = self.unstick_time
        embed_title = self.embed_title.value
        embed_description = self.embed_description.value

        await asmdb.stick(
            channel_id=channel_id,
            embed_title=embed_title,
            embed_description=embed_description,
            stick_time=stick_time,
            unstick_time=unstick_time,
        )

        embed = discord.Embed(
            title=embed_title,
            description=embed_description,
            colour=discord.Colour.green(),
        )
        message = f"Advstick has been successfully scheduled to stick at <t:{stick_time}:F> (<t:{stick_time}:R>) and unstick at <t:{unstick_time}:F> (<t:{unstick_time}:R>)"
        await interaction.send(content=message, embed=embed, ephemeral=True)


@bot.slash_command(
    name="advstick",
    description="sends a message in advance and automatically sticks it.",
    guild_ids=[GUILD_ID],
)
async def advstick(
    interaction: discord.Interaction,
    channel: discord.TextChannel = discord.SlashOption(
        name="channel",
        description="Which channel do you want the message to be stuck on?",
        required=True,
    ),
    stick_time: str = discord.SlashOption(
        name="sticktime", description="Message Auto-Stick Time (Epoch)", required=True
    ),
    unstick_time: str = discord.SlashOption(
        name="unsticktime",
        description="Message Auto-Unstick Time (Epoch)",
        required=True,
    ),
):

    await interaction.response.send_modal(
        modal=Stick_Message(str(channel.id), stick_time, unstick_time)
    )
