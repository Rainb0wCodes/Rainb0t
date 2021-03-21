import os, sys, math, discord, inspect
from discord.ext import commands
if not os.path.isfile("config.py"):
	sys.exit("'config.py' not found! Please add it and try again.")
else:
	import config

HELP_PAGE_SIZE = 5

def get_command_signature(func):
    strings = [func.__name__]
    data = inspect.signature(func)

    for parameter in data.parameters:
        if parameter in ('ctx', 'context', 'self'):
            continue

        if data.parameters[parameter].default == inspect.Parameter.empty:
            strings.append(f"<{parameter.replace('_', ' ')}>")
        else:
            strings.append(f"[{parameter}]")

    return ' '.join(strings)

class Help(commands.Cog, name="help"):
	def __init__(self, bot):
		self.bot = bot

	@commands.command(aliases=['cmds', 'commands'])
	async def help(self, ctx: commands.Context, page: int = 1):
		"""Explains how to use the different Rainb0t commands."""
		total_pages = int(math.ceil(len(self.bot.commands) / HELP_PAGE_SIZE))

		embed = discord.Embed(title="Help", color=config.EMBED_COLOR)
		embed.set_footer(
		    text=f"Page {page}/{total_pages} \u2022 Bot by Rainb0wCodes_484#4288")

		start = (page - 1) * HELP_PAGE_SIZE

		commands = sorted(self.bot.commands, key=lambda command: command.name)

		for command in commands[start:start + HELP_PAGE_SIZE]:
			embed.add_field(name=get_command_signature(
			    command.callback), value=command.help, inline=False)

		await ctx.send(embed=embed)

def setup(bot):
	bot.add_cog(Help(bot))
