""""
Copyright © Krypton 2021 - https://github.com/kkrypt0nn
Copyright © Rainb0wCodes 2021 - https://github.com/Rainb0wCodes
Description:
This is my personal Discord bot, Rainb0t

Version: 0.1.0
"""

import discord, asyncio, os, platform, sys, json
from discord.ext.commands import Bot, when_mentioned_or, has_permissions, Context, MissingPermissions, BotMissingPermissions, BucketType, CommandOnCooldown, CommandNotFound
from discord.ext import commands
if not os.path.isfile("config.py"):
	sys.exit("'config.py' not found! Please add it and try again.")
else:
	import config

"""	
Setup bot intents (events restrictions)
For more information about intents, please go to the following websites:
https://discordpy.readthedocs.io/en/latest/intents.html
https://discordpy.readthedocs.io/en/latest/intents.html#privileged-intents


Default Intents:
intents.messages = True
intents.reactions = True
intents.guilds = True
intents.emojis = True
intents.bans = True
intents.guild_typing = False
intents.typing = False
intents.dm_messages = False
intents.dm_reactions = False
intents.dm_typing = False
intents.guild_messages = True
intents.guild_reactions = True
intents.integrations = True
intents.invites = True
intents.voice_states = False
intents.webhooks = False

Privileged Intents (Needs to be enabled on dev page):
intents.presences = True
intents.members = True
"""

intents = discord.Intents.default()

"""Gets the assigned bot prefix for a guild."""
def get_prefix(guild: discord.Guild):
    if not str(guild.id) in prefixes:
        return ';'

    return prefixes[str(guild.id)]

"""Gets the prefixes for a message"""
def get_prefixes(bot: Bot, message: discord.Message):
	if message.guild:
		return when_mentioned_or(get_prefix(message.guild))(bot, message)
	else:
		return when_mentioned_or(';')(bot, message)

def snake_case_to_title_case(string):
    chars = list(string.replace('_', ' '))
    for i, char in enumerate(chars):
        if i == 0 or chars[i - 1] == ' ':
            chars[i] = chars[i].upper()

    return ''.join(chars)

def load_data():
    global prefixes

    try:
        with open('./prefixes.json', 'r') as fd:
            prefixes = json.load(fd)
            print(f"Loaded prefixes for {len(prefixes)} servers!")
    except IOError:
        with open('./prefixes.json', 'w') as fd:
            json.dump({}, fd)

bot = Bot(command_prefix=config.BOT_PREFIX, intents=intents)

# The code in this even is executed when the bot is ready
@bot.event
async def on_ready():
	bot.loop.create_task(status_task())
	print(f"Logged in as {bot.user.name}")
	print(f"Discord.py API version: {discord.__version__}")
	print(f"Python version: {platform.python_version()}")
	print(f"Running on: {platform.system()} {platform.release()} ({os.name})")
	print("-------------------")

# Setup the game status task of the bot
async def status_task():
	while True:
		await bot.change_presence(activity=discord.Activity(name="you", type=discord.ActivityType.watching))
		await asyncio.sleep(60)
		await bot.change_presence(activity=discord.Activity(name="over Discord", type=discord.ActivityType.watching))
		await asyncio.sleep(60)
		await bot.change_presence(activity=discord.Game(f"{config.BOT_PREFIX} help"))
		await asyncio.sleep(60)
		await bot.change_presence(activity=discord.Activity(name="all of us", type=discord.ActivityType.watching))
		await asyncio.sleep(60)

# Removes the default help command of discord.py to be able to create our custom help command.
bot.remove_command("help")

if __name__ == "__main__":
	for extension in config.STARTUP_COGS:
		try:
			bot.load_extension(extension)
			extension = extension.replace("cogs.", "")
			print(f"Loaded extension '{extension}'")
		except Exception as e:
			exception = f"{type(e).__name__}: {e}"
			extension = extension.replace("cogs.", "")
			print(f"Failed to load extension {extension}\n{exception}")

@bot.command()
@has_permissions(manage_guild=True)
async def prefix(ctx: Context, *, new_prefix: str):
    prefixes[str(ctx.guild.id)] = new_prefix

    embed = discord.Embed(
        title="Prefix set", description=f"Prefix set to {new_prefix}", color=config.EMBED_COLOR)

    await ctx.send(embed=embed)

    with open('./prefixes.json', 'w') as fd:
        json.dump(prefixes, fd)

# The code in this event is executed every time someone sends a message, with or without the prefix
@bot.event
async def on_message(message: discord.Message):
	# Ignores if a command is being executed by a bot or by the bot itself
	if message.author == bot.user or message.author.bot:
		return
	else:
		if message.author.id not in config.BLACKLIST:
			# Process the command if the user is not blacklisted
			await bot.process_commands(message)
		else:
			# Send a message to let the user know he's blacklisted
			context = await bot.get_context(message)
			embed = discord.Embed(
				title="You're blacklisted!",
				description="Ask the owner to remove you from the list if you think it's not normal.",
				color=0xFF0000
			)
			await context.send(embed=embed)

@bot.event
async def on_command_error(ctx: Context, error: Exception):
    if isinstance(error, MissingPermissions):
        missing_perms = error.missing_perms
        missing_perms = map(lambda permission: snake_case_to_title_case(
            permission.replace("guild", "server")), missing_perms)
        missing_perms = list(missing_perms)

        embed = discord.Embed(title="Missing Permissions", color=0xde1b1b, description="<:xmark:823005434629586974> Error! You are missing the " +
                              (f"{', '.join(missing_perms[:-1])} and {missing_perms[-1]}" if len(missing_perms) > 1 else missing_perms[0]) +
                              f" permission{'s' if len(missing_perms) > 1 else ''}!")
        await ctx.send(embed=embed)
        return

    if isinstance(error, BotMissingPermissions):
        missing_perms = error.missing_perms
        missing_perms = list(map(lambda permission: snake_case_to_title_case(
            permission.replace("guild", "server")), missing_perms))

        embed = discord.Embed(title="Missing Permissions", color=0xde1b1b, description="<:xmark:823005434629586974> Error! I need the " +
                              (f"{', '.join(missing_perms[:-1])} and {missing_perms[-1]}" if len(missing_perms) > 1 else missing_perms[0]) +
                              f" permission{'s' if len(missing_perms) > 1 else ''} to run this command.")
        await ctx.send(embed=embed)
        return

    if isinstance(error, CommandOnCooldown):
        embed = discord.Embed(
            title="Cooldown!", color=0xde1b1b,
            description=f"<:xmark:823005434629586974> Error! You are on cooldown." +
            f"You can use the `{ctx.command}` command again in {format_seconds(error.retry_after)}."
        )
        await ctx.send(embed=embed)
        return

    if isinstance(error, CommandNotFound):
        embed = discord.Embed(
            title="Command doesn't exist!", color=0xde1b1b,
            description=f"<:xmark:823005434629586974> Error! That command doesn't exist!"
        )
        await ctx.send(embed=embed)
        return

    embed = discord.Embed(title="<:xmark:823005434629586974> Unknown error", color=0xde1b1b,
                          description='```py\n' + repr(error) + '\n```')
    await ctx.send(embed=embed)

prefixes = {}
load_data()

# Run the bot with the token
bot.run(config.TOKEN)
