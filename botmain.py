import discord
from discord.ext import commands
import asyncio

# ============================================================
#                        CONFIG
# ============================================================
TOKEN = "MTU1NTUxODMzNDE2NDc5OTYwOA.G-h3D1.JCpUvhaVHXEquk88ioILBr_RHGMUX_m-kumH3g"                     # <-- Paste your NEW token here

# --- Poll command ---
POLL_COMMAND = "+k^$8$3Sn3%1$J<$(!>)!S(%$"
MIN_VOTES = 5
POLL_TITLE = "🚀 Server Startup Poll"
POLL_DESCRIPTION = "This is a server startup session for **SCP:Roleplay**"
POLL_FOOTER = "This poll is managed by the Ownership / SSUH team"
POLL_COLOR = discord.Color.blurple()
EMBED_IMAGE_URL = "attachment://startup_poll.png"
IMAGE_PATH = "startup_poll.png"
VOTE_EMOJI = "✅"

# --- Startup announcement command ---
STARTUP_COMMAND = "+k349616swus726796s12w7126w762"
STARTUP_CHANNEL_ID = 1555471425614258296           # Your channel ID
STARTUP_TITLE = "🟢 Server has been opened!"
SERVER_NAME = "Site-301 \"Vestige\""
STARTUP_NOTES = (
    "Server may be slightly delayed/stopped under unknown circumstances.\n"
    "Thank you for sticking with Site 301!"
)
STARTUP_COLOR = discord.Color.green()

# --- Shutdown command ---
SHUTDOWN_COMMAND = "+k982671s128971727ws"          # Base trigger
SHUTDOWN_CHANNEL_ID = 1555471425614258296          # Where to post the shutdown embed
SHUTDOWN_TITLE = "🔴 Server has shutdowned!"
SHUTDOWN_EXTRA = "Stay tuned for another ssu! "
SHUTDOWN_EXTRA = "HPC:Highest Player Count"
SHUTDOWN_EXTRA = "Thanks for attending the server startup!"
SHUTDOWN_DEFAULT_HPC = "N/A"
SHUTDOWN_COLOR = discord.Color.dark_red()
# ============================================================

# --- Bot setup ---
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")


# ============================================================
#  GRADIENT BANNER GENERATOR (black ↔ white gradient)
# ============================================================
def make_gradient_banner(width: int = 600, height: int = 120,
                         left_rgb=(0, 0, 0), right_rgb=(255, 255, 255)):
    """Create a horizontal gradient PNG from left_rgb to right_rgb."""
    from PIL import Image
    img = Image.new("RGB", (width, height))
    pixels = img.load()
    for x in range(width):
        t = x / (width - 1)
        r = int(left_rgb[0] + (right_rgb[0] - left_rgb[0]) * t)
        g = int(left_rgb[1] + (right_rgb[1] - left_rgb[1]) * t)
        b = int(left_rgb[2] + (right_rgb[2] - left_rgb[2]) * t)
        for y in range(height):
            pixels[x, y] = (r, g, b)
    img.save("gradient_banner.png")
    return "gradient_banner.png"


@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    content = message.content.strip()

    # ---------------------------------------------------------
    # POLL COMMAND
    # ---------------------------------------------------------
    if content == POLL_COMMAND:
        executor = message.author

        embed = discord.Embed(
            title=POLL_TITLE,
            description=POLL_DESCRIPTION,
            color=POLL_COLOR
        )
        embed.add_field(name="Executed By", value=executor.mention, inline=False)
        embed.add_field(
            name="Authority",
            value="This is executed by the **Ownership / SSUH team**.",
            inline=False
        )
        embed.add_field(
            name="Vote Requirement",
            value=f"A minimum of **{MIN_VOTES} {VOTE_EMOJI}** is needed to start a session.",
            inline=False
        )
        embed.set_footer(text=POLL_FOOTER)

        try:
            file = discord.File(IMAGE_PATH, filename="startup_poll.png")
            embed.set_image(url=EMBED_IMAGE_URL)
            poll_message = await message.channel.send(
                content="@everyone",
                embed=embed,
                file=file,
                allowed_mentions=discord.AllowedMentions(everyone=True)
            )
        except FileNotFoundError:
            poll_message = await message.channel.send(
                content="@everyone",
                embed=embed,
                allowed_mentions=discord.AllowedMentions(everyone=True)
            )
            await message.channel.send(f"⚠️ Image `{IMAGE_PATH}` not found — posted without it.")
        except discord.Forbidden:
            await message.channel.send("❌ I don't have permission to ping everyone here!")
            return

        await poll_message.add_reaction(VOTE_EMOJI)

        try:
            await message.delete()
        except (discord.Forbidden, discord.NotFound):
            pass

        bot.loop.create_task(watch_votes(poll_message, MIN_VOTES))

    # ---------------------------------------------------------
    # STARTUP ANNOUNCEMENT COMMAND
    # ---------------------------------------------------------
    elif content == STARTUP_COMMAND:
        executor = message.author
        channel = bot.get_channel(STARTUP_CHANNEL_ID)
        if channel is None:
            try:
                channel = await bot.fetch_channel(STARTUP_CHANNEL_ID)
            except discord.NotFound:
                await message.channel.send("❌ Startup channel not found.")
                return

        embed = discord.Embed(
            title=STARTUP_TITLE,
            description=(
                f"**Executed by:** {executor.mention}\n\n"
                f"The server is now online and its name is\n"
                f"**{SERVER_NAME}**\n\n"
                f"{STARTUP_NOTES}"
            ),
            color=STARTUP_COLOR
        )
        embed.set_footer(text="Ownership / SSUH Team")

        # Gradient banner as top image
        try:
            make_gradient_banner()
            banner = discord.File("gradient_banner.png", filename="gradient_banner.png")
            embed.set_image(url="attachment://gradient_banner.png")
            await channel.send(
                content="@everyone",
                embed=embed,
                file=banner,
                allowed_mentions=discord.AllowedMentions(everyone=True)
            )
        except Exception:
            await channel.send(
                content="@everyone",
                embed=embed,
                allowed_mentions=discord.AllowedMentions(everyone=True)
            )

        try:
            await message.delete()
        except (discord.Forbidden, discord.NotFound):
            pass

    # ---------------------------------------------------------
    # SHUTDOWN COMMAND  ( +k982671s128971727ws [optional HPC] )
    # ---------------------------------------------------------
    elif content.startswith(SHUTDOWN_COMMAND):
        # Extract the rest of the message after the command
        tail = content[len(SHUTDOWN_COMMAND):].strip()

        # Determine HPC value
        hpc_value = SHUTDOWN_DEFAULT_HPC
        if tail:
            if tail.isdigit():
                num = int(tail)
                if 0 <= num <= 250:
                    hpc_value = str(num)
                else:
                    await message.channel.send("❌ HPC must be a number between 0 and 250.")
                    return
            else:
                await message.channel.send("❌ Invalid HPC — please provide a number (0–250).")
                return

        channel = bot.get_channel(SHUTDOWN_CHANNEL_ID)
        if channel is None:
            try:
                channel = await bot.fetch_channel(SHUTDOWN_CHANNEL_ID)
            except discord.NotFound:
                await message.channel.send("❌ Shutdown channel not found.")
                return

        executor = message.author
        embed = discord.Embed(
            title=SHUTDOWN_TITLE,
            description=(
                f"**HPC:** {hpc_value}\n\n"
                f"{SHUTDOWN_EXTRA}"
            ),
            color=SHUTDOWN_COLOR
        )
        embed.set_footer(text=f"Executed by {executor.display_name} • Ownership / SSUH Team")

        # Gradient banner on the shutdown embed too
        try:
            make_gradient_banner()
            banner = discord.File("gradient_banner.png", filename="gradient_banner.png")
            embed.set_image(url="attachment://gradient_banner.png")
            await channel.send(
                content="@everyone",
                embed=embed,
                file=banner,
                allowed_mentions=discord.AllowedMentions(everyone=True)
            )
        except Exception:
            await channel.send(
                content="@everyone",
                embed=embed,
                allowed_mentions=discord.AllowedMentions(everyone=True)
            )

        try:
            await message.delete()
        except (discord.Forbidden, discord.NotFound):
            pass

    await bot.process_commands(message)


async def watch_votes(poll_message: discord.Message, min_votes: int):
    await asyncio.sleep(2)
    announced = False
    while True:
        await asyncio.sleep(5)
        try:
            poll_message = await poll_message.channel.fetch_message(poll_message.id)
        except discord.NotFound:
            return
        for reaction in poll_message.reactions:
            if str(reaction.emoji) == VOTE_EMOJI:
                count = reaction.count - 1
                if count >= min_votes and not announced:
                    embed = discord.Embed(
                        title="✅ Vote Threshold Reached!",
                        description=(
                            f"The poll has reached **{count}/{min_votes}** votes.\n"
                            "The server startup session may now begin."
                        ),
                        color=discord.Color.green()
                    )
                    await poll_message.reply(embed=embed, mention_author=False)
                    announced = True
                break


bot.run(TOKEN)