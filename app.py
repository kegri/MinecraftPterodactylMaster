#!/home/tony/python/tonymc/venv/bin/python3

import discord
from discord.ext import tasks, commands
#from mcstatus import MinecraftServer
import random
from panel_cog import panel_cog
from mcstatus_cog import mcstatus_cog
import logging
import asyncio
import logging.handlers
# https://www.zopatista.com/python/2019/05/11/asyncio-logging/
try:
    # Python 3.7 and newer, fast reentrant implementation
    # without task tracking (not needed for that when logging)
    from queue import SimpleQueue as Queue
except ImportError:
    from queue import Queue
from io import BytesIO
from config import *
from os.path import dirname, realpath

loop = asyncio.get_event_loop()

#server = MinecraftServer(config_ip, config_port)

#pclient = PterodactylClient(config_panel_url, config_panel_token)

description = '''Bot written by Kegrine to start/stop the Minecraft server based on current activity and user requests for server uptime.'''

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=config_command_prefix,
                   description=description,
                   intents=intents)
# https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#discord.ext.commands.when_mentioned_or

bot.remove_command('help')
logger = None
#discord_logger = logging.getLogger("discord")

@bot.event
async def on_ready():
    logger.info("Logged in as {0} with ID: {1}".format(
        bot.user.name, bot.user.id))

@bot.event
async def on_message(message: discord.Message):
    # Make sure it only works in your guild(s) in case someone adds the bot themselves to another guild
    if message.guild.id in config_allowed_guilds:
        await bot.process_commands(message)

@bot.event
async def on_reaction_add(reaction: discord.Reaction, user: discord.User):
    if user.id != bot.user.id:
        panel_info = bot.get_cog("panel_cog")
        if panel_info is not None:
            motion = panel_info.current_vote_action
            if motion is not None:
                if user.id in config_admin_users:
                    logger.info("{0} reaction admin'd server: {1}.".format(str(user), motion))
                    await panel_info.power_action(motion)
                    await reaction.message.add_reaction("👌")
                if user.id not in panel_info.voters:
                    if reaction.message.id in panel_info.votable_messages:
                        panel_info.voters.append(user.id)
                        
                        if len(panel_info.voters) >= config_votes_needed:
                            await reaction.message.edit(content=config_reply_need_more_votes.format(config_votes_needed-len(panel_info.voters), motion))
                            await panel_info.vote_passed(reaction.message.channel, motion)
                            await panel_info.power_action(motion)
                        else:
                            await reaction.message.edit(content=config_reply_need_more_votes.format(config_votes_needed-len(panel_info.voters), motion))

@bot.event
async def on_ready():
    await bot.add_cog(mcstatus_cog(bot, get_status))
    await bot.add_cog(panel_cog(bot))
                    

@bot.command()
async def help(ctx):
    embed = embed = discord.Embed(title="Bot Help", color=config_embed_color)
    embed.add_field(name="help", value="This command right here!", inline=False)
    embed.add_field(name="restart", value="(aliases: server_restart, reboot)\nRestarts the server immediately after vote passes", inline=False)
    embed.add_field(name="stop", value="(aliases: server\_off, off, turn\_off, shutdown)\nWill stop the server immediately after vote passes\n\nAdmins can run `{0}stop kill` to kill the server. __Do not kill unless absolutely necessary__".format(config_command_prefix), inline=False)
    embed.add_field(name="start", value="(aliases: server\_on, on, turn\_on)\nWill start the server immediately after vote passes", inline=False)
    embed.add_field(name="status", value="Check and return the current (last known) status of the server.\nAlso shows currently connected players", inline=False)
    embed.add_field(name="How voting works", value="When someone types in a command (e.g. `{0}restart` or `{0}on`), it will start a vote for **{1}** seconds. If in that time a total of **{2}** people type the same command, it will do that action!".format(config_command_prefix, config_vote_timeout, config_votes_needed), inline=False)
    if config_shutdown_empty_server:
        embed.add_field(name="Auto shutdown", value="This bot checks every so often to see if the server is empty. If it is, it will be automatically shut down.", inline=False)
    if config_bot_source_code.strip() != "":
        embed.add_field(name="Source Code", value=config_bot_source_code, inline=False)
    #embed.set_footer(text=config_custom_footer)
    embed.add_field(name="Server Info", value=config_custom_footer, inline=False)
    await ctx.send(embed=embed)


@bot.command()
async def status(ctx):
    """Check and return the current (last known) status of the server."""
    embed = discord.Embed(title="Server Status", color=config_embed_color)
    mcstatus_info = bot.get_cog("mcstatus_cog")
    panel_info = bot.get_cog("panel_cog")
    current_status = await get_status()
    # Default icon in case no other image is set
    filepath = "{0}/images/owo.png".format(dirname(realpath(__file__)))
    file = discord.File(filepath, "icon.png")
    if mcstatus_info is not None and panel_info is not None:
        if current_status == "online":
            if panel_info.server_power_status == "online":
                cpu, ram = await panel_info.get_cpu_and_ram()
                cpu = "{0}%".format(cpu)
                ram = "{0}GB".format(ram)
                embed.add_field(name="CPU", value=cpu, inline=True)
                embed.add_field(name="RAM", value=ram, inline=True)
            if mcstatus_info.server_power_status == "online":
                if mcstatus_info.decoded_favicon is not None:
                    fake_file = BytesIO(mcstatus_info.decoded_favicon)
                    file = discord.File(fake_file, "icon.png")
                current, max = await mcstatus_info.get_players_and_max()
                full_value = "{0}/{1} Players".format(current, max)
                if current > 0:
                    full_value += "\n-----"
                    for player in mcstatus_info.server_status.players.sample:
                        full_value += "\n{0}".format(player.name)
                embed.add_field(name="Players", value=full_value, inline=False)
        else:
            if current_status == "starting":
                embed.add_field(name="Server Starting", value="Please wait while the server boots.", inline=False)
            elif current_status == "stopping":
                embed.add_field(name="Server Stopping", value="Please wait while the server shuts down.", inline=False)
                filepath = "{0}/images/ganomuslogo.jpeg".format(dirname(realpath(__file__)))
                file = discord.File(filepath, "icon.png")
            else:
                filepath = "{0}/images/ganomuslogo.jpeg".format(dirname(realpath(__file__)))
                file = discord.File(filepath, "icon.png")
                example_command = "You can type `{0}on` (or its aliases) to start the server yourself!".format(config_command_prefix)
                embed.add_field(name="Server Offline", value=example_command, inline=False)
    else:
        logger.error("Either MCStatus or Panel cog was unable to talk!")
        embed.add_field(name="Internal Bot Error!", value="Can't talk to panel?", inline=False)
        filepath = "{0}/images/ganomuslogo.jpeg".format(dirname(realpath(__file__)))
        file = discord.File(filepath, "icon.png")
    
    embed.set_thumbnail(url="attachment://icon.png")
    embed.add_field(name="Server Info", value=config_custom_footer, inline=False)
    # await self.bot.say(embed=embed)

    response = await ctx.send(file=file, embed=embed)
    #await bot.change_presence(activity=discord.Game("hi"), status=discord.Status.dnd)

async def get_status():
    mcstatus_info = bot.get_cog("mcstatus_cog")
    panel_info = bot.get_cog("panel_cog")
    if mcstatus_cog is not None and panel_cog is not None:
        if mcstatus_info.server_power_status == "online":
            return "online"
        else:
            acceptable_panel_statuses = ["offline", "online", "starting", "stopping", "error"]
            if panel_info.server_power_status in acceptable_panel_statuses:
                return panel_info.server_power_status
    else:
        return "error"
        logger.error("Cogs not responding when getting status")


#status = server.status()
# for pl in status.players.sample:
#    print(pl.name)
#print("The server has {0} players and replied in {1} ms".format(status.players, status.latency))
# print(pclient.client.list_servers())

class LocalQueueHandler(logging.handlers.QueueHandler):
    def emit(self, record: logging.LogRecord) -> None:
        # Removed the call to self.prepare(), handle task cancellation
        try:
            self.enqueue(record)
        except asyncio.CancelledError:
            raise
        except Exception:
            self.handleError(record)

def setup_logging_queue() -> None:
    """Move log handlers to a separate thread.

    Replace handlers on the root logger with a LocalQueueHandler,
    and start a logging.QueueListener holding the original
    handlers.

    """
    queue = Queue()
    

    handlers: List[logging.Handler] = []

    handler = LocalQueueHandler(queue)
    logger.addHandler(handler)
    for h in logger.handlers[:]:
        if h is not handler:
            logger.removeHandler(h)
            handlers.append(h)

    listener = logging.handlers.QueueListener(
        queue, *handlers, respect_handler_level=True
    )
    listener.start()

if __name__ == "__main__":
    # Configuring logging
    logger = logging.getLogger("tonymc")
    logger.setLevel(logging.DEBUG)
    filepath = "{0}/bot.log".format(dirname(realpath(__file__)))
    file_handler = logging.FileHandler(filepath)
    file_handler.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    log_formatter = logging.Formatter(
        '%(asctime)s:%(levelname)s:%(name)s: %(message)s')
    file_handler.setFormatter(log_formatter)
    console_handler.setFormatter(log_formatter)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    setup_logging_queue()
    #discord_logger.setLevel(logging.DEBUG)
    #discord_handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
    #discord_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    #discord_logger.addHandler(discord_handler)


    bot.run(config_discord_token)