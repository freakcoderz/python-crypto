import discord
from discord.ext import commands
import asyncio
from itertools import cycle
from utils import output, parsing, checks, mysql_module, helpers
import os
import traceback
import database
import re

config = parsing.parse_json('config.json')
skip_cogs=config['skip_cogs']

Mysql = mysql_module.Mysql()

bot = commands.Bot(command_prefix=config['prefix'], description=config["description"])

try:
    os.remove("log.txt")
except FileNotFoundError:
    pass

startup_extensions = os.listdir("./cogs")
if "__pycache__" in startup_extensions:
    startup_extensions.remove("__pycache__")
startup_extensions = [ext.replace('.py', '') for ext in startup_extensions]
loaded_extensions = []

startup_extensions=[x for x in startup_extensions if x not in skip_cogs]

@bot.event
async def on_ready():
    output.info("Loading {} extension(s)...".format(len(startup_extensions)))

    for extension in startup_extensions:
        try:
            bot.load_extension("cogs.{}".format(extension.replace(".py", "")))
            loaded_extensions.append(extension)

        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            output.error('Failed to load extension {}\n\t->{}'.format(extension, exc))
    output.success('Successfully loaded the following extension(s): {}'.format(', '.join(loaded_extensions)))
    output.info('You can now invite the bot to a server using the following link: https://discordapp.com/api/oauth2/authorize?client_id=477114120299085854&permissions=0&scope=bot'.format(bot.user.id))
    nameRan = ['Deposits disabled', 'Support ending']
    await bot.change_presence(game=discord.Game(name='Closing in 1 hour', type=2))

@bot.event
async def on_message(message):
    # disregard messages sent by our own bot
    if message.author.id == bot.user.id:
        return

    # check if the owner is registered
    # must be done to add an entry to the db and initialize the db
    owner = config["owners"]
    for ids in owner:
        if Mysql.get_user(ids) is None:
            if message.author.id == ids:
                Mysql.register_user(ids)
                
    # check if the message is from a banned server
    if message.server is not None:
        if Mysql.check_for_server_status(message.server.id) == 2:
            return

    # check if staking account is set up
    staking_account = config["stake_bal"]
    if Mysql.get_staking_user(staking_account) is None:
        Mysql.register_user(staking_account)

    # check if treasury account is set up
    treasury_account = config["treasurer"]
    if Mysql.get_staking_user(treasury_account) is None:
        Mysql.register_user(treasury_account)

    # check if donation account is set up
    donate_account = config["donation"]
    if Mysql.get_staking_user(donate_account) is None:
        Mysql.register_user(donate_account)

    # check if game account is set up
    game_account = config["game_bal"]
    if Mysql.get_staking_user(game_account) is None:
        Mysql.register_user(game_account)

    # users that are not registered will be caught below
    # continue if the message is not from the bot
    if not message.author.bot:
        #config register keyword
        rkeyword = str(config["register_keyword"])
        prefix = str(config["prefix"])
        #rkeywordcall is the register command for users not registered
        rkeywordcall = prefix + rkeyword
        coin_name = str(config["currency_symbol"])
        #authid is the unique discord id number for the user that send the message to the server
        authid = message.author.id
        #check if the message author is in the database (meaning they are registered)
        if Mysql.get_user(authid) is None:
            #if they they are not it the database but send the
            if str(message.content).startswith(rkeywordcall) is True:
                Mysql.register_user(authid)
                await bot.send_message(message.channel, '{} You are Now Registered. :tada:'.format(message.author.mention))
                await bot.send_message(message.author, 'Thank You for registering. Use {}deposit to check your {} deposit address'.format(prefix, coin_name))
                return
            elif str(message.content).startswith(prefix) is True:
                await bot.send_message(message.channel, '{} You are NOT registered. Type **{}** to begin.'.format(message.author.mention, rkeywordcall))
                return
        # check if user exists
        elif Mysql.get_user(authid) is not None and Mysql.check_soakme(authid) == 2: 
            if str(message.content).startswith(prefix) is True:
            # tell them they are banned and ignore them
                await bot.send_message(message.channel, '{} You were banned from bot use. Please contact an Aevo admin if you feel this was an error.'.format(message.author.mention))
                return
        else:
            if Mysql.user_last_msg_check(message.author.id, message.content, helpers.is_private_dm(bot, message.channel)) == False:
                return 
            await bot.process_commands(message)

async def send_cmd_help(ctx):
    if ctx.invoked_subcommand:
        pages = bot.formatter.format_help_for(ctx, ctx.invoked_subcommand)
        for page in pages:
            em = discord.Embed(title="Missing args :x:",
                               description=page.strip("```").replace('<', '[').replace('>', ']'),
                               color=discord.Color.red())
            await bot.send_message(ctx.message.channel, embed=em)
    else:
        pages = bot.formatter.format_help_for(ctx, ctx.command)
        for page in pages:
            em = discord.Embed(title="Missing args :x:",
                               description=page.strip("```").replace('<', '[').replace('>', ']'),
                               color=discord.Color.red())
            await bot.send_message(ctx.message.channel, embed=em)

@bot.command(pass_context=True, hidden=True)
@commands.check(checks.is_owner)
async def shutdown(ctx):
    """Shut down the bot [ADMIN ONLY]"""
    author = str(ctx.message.author)

    try:
        await bot.say("Shutting down...")
        await bot.logout()
        bot.loop.stop()
        output.info('{} has shut down the bot...'.format(author))

    except Exception as e:
        exc = '{}: {}'.format(type(e).__name__, e)
        output.error('{} has attempted to shut down the bot, but the following '
                     'exception occurred;\n\t->{}'.format(author, exc))

@bot.command(pass_context=True, hidden=True)
@commands.check(checks.is_owner)
async def restart(ctx):
    """Restart the bot [ADMIN ONLY]"""
    author = str(ctx.message.author)

    try:
        await bot.say("Restarting...")
        await bot.logout()
        bot.loop.stop()
        output.info('{} has restarted the bot...'.format(author))
        os.system('sh restart.sh')

    except Exception as e:
        exc = '{}: {}'.format(type(e).__name__, e)
        output.error('{} has attempted to restart the bot, but the following '
                     'exception occurred;\n\t->{}'.format(author, exc))


@bot.command(pass_context=True, hidden=True)
@commands.check(checks.is_owner)
async def load(ctx, module: str):
    """Load a cog located in /cogs [ADMIN ONLY]"""
    author = str(ctx.message.author)
    module = module.strip()

    try:
        bot.load_extension("cogs.{}".format(module))
        output.info('{} loaded module: {}'.format(author, module))
        startup_extensions.append(module)
        await bot.say("Successfully loaded {}.py".format(module))

    except Exception as e:
        exc = '{}: {}'.format(type(e).__name__, e)
        output.error('{} attempted to load module \'{}\' but the following '
                     'exception occured;\n\t->{}'.format(author, module, exc))
        await bot.say('Failed to load extension {}\n\t->{}'.format(module, exc))


@bot.command(pass_context=True, hidden=True)
@commands.check(checks.is_owner)
async def unload(ctx, module: str):
    """Unload any loaded cog [ADMIN ONLY]"""
    author = str(ctx.message.author)
    module = module.strip()

    try:
        bot.unload_extension("cogs.{}".format(module))
        output.info('{} unloaded module: {}'.format(author, module))
        startup_extensions.remove(module)
        await bot.say("Successfully unloaded {}.py".format(module))

    except Exception as e:
        exc = '{}: {}'.format(type(e).__name__, e)
        await bot.say('Failed to load extension {}\n\t->{}'.format(module, exc))


@bot.command(hidden=True)
@commands.check(checks.is_owner)
async def loaded():
    """List loaded cogs [ADMIN ONLY]"""
    string = ""
    for cog in loaded_extensions:
        string += str(cog) + "\n"

    await bot.say('Currently loaded extensions:\n```{}```'.format(string))
    
@bot.command(hidden=True)
@commands.check(checks.is_admin)
async def guilds():
    """Provides list of servers the bot is in [OWNER ONLY]"""
    servers = list(bot.servers)
    await bot.say(f"Connected on {str(len(servers))} servers:")
    for server in servers:
        await bot.say('\n' + server.name + ' ' + server.id)
    
@bot.command(hidden=True)
@commands.check(checks.is_owner)
async def leave(server):
    toleave = bot.get_server(server)
    if(toleave):
        await bot.leave_server(toleave)
        await bot.say("I have left that server")
    else:
        await bot.say("I am not in that server")

@bot.event
async def on_server_join(server):
    output.info("Added to {0}".format(server.name))
    Mysql.add_server(server)
    for channel in server.channels:
        Mysql.add_channel(channel)


@bot.event
async def on_server_leave(server):
    Mysql.remove_server(server)
    output.info("Removed from {0}".format(server.name))


@bot.event
async def on_channel_create(channel):
    if isinstance(channel, discord.PrivateChannel):
        return
    Mysql.add_channel(channel)
    output.info("Channel {0} added to {1}".format(channel.name, channel.server.name))
    
#@bot.event
#async def on_stake(ctx, amount):
    #Mysql.check_for_updated_mining_balance(ctx, amount)
    #output.info("Stake sent to elligible users", amount)

@bot.event
async def on_channel_delete(channel):
    Mysql.remove_channel(channel)
    output.info("Channel {0} deleted from {1}".format(channel.name, channel.server.name))


@bot.event
async def on_command_error(error, ctx):
    channel = ctx.message.channel
    if isinstance(error, commands.MissingRequiredArgument):
        await send_cmd_help(ctx)
    elif isinstance(error, commands.BadArgument):
        await send_cmd_help(ctx)
    elif isinstance(error, commands.CommandInvokeError):
        output.error("Exception in command '{}', {}".format(ctx.command.qualified_name, error.original))
        oneliner = "Error in command '{}' - {}: {}\nIf this issue persists, Please report it in the support server.".format(
            ctx.command.qualified_name, type(error.original).__name__, str(error.original))
        await ctx.bot.send_message(channel, oneliner)

database.run()
bot.run(config["discord"]["token"])
bot.loop.close()
