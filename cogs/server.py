import discord, os, itertools
from discord.ext import commands
from utils import parsing, checks, mysql_module
from discord import User

mysql = mysql_module.Mysql()


class Server:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, hidden=True)
    @commands.check(checks.in_server)
    @commands.check(checks.is_admin)
    async def allowsoak(self, ctx, enable: bool):
        """
        Enable and disable the soak feature [ADMIN ONLY]
        """
        mysql.set_soak(ctx.message.server, int(enable))
        if enable:
            await self.bot.say("Ok! Soaking is now enabled! :white_check_mark:")
        else:
            await self.bot.say("Ok! Soaking is now disabled! :no_entry_sign:")

    @commands.command(pass_context=True)
    @commands.check(checks.in_server)
    @commands.check(checks.is_admin)
    async def checksoak(self, ctx):
        """
        Checks if soak is available on the server
        """
        result_set = mysql.check_soak(ctx.message.server)
        if result_set:
            await self.bot.say("Soaking is enabled! :white_check_mark:")
        else:
            await self.bot.say("Soaking is disabled! :no_entry_sign:")

    @commands.command(pass_context=True)
    @commands.check(checks.is_admin)
    async def userban(self, ctx, user: User):
        """
        Ban a user from the bot (ADMIN ONLY)
        """
        snowflake = user.id
        if mysql.check_for_user(snowflake):
            if mysql.check_soakme(snowflake) == 2:
                await self.bot.say("Member: {} is already BANNED.".format(user.mention))
            else:
                mysql.set_soakme(snowflake, 2)
                await self.bot.say("Member: {} is now marked as BANNED.".format(user.mention))
        else:
            await self.bot.say("Member: {} is not registered with this bot. The member will now be registered and marked as banned".format(user.mention))
            mysql.register_user(snowflake)
            mysql.set_soakme(snowflake, 2)
            await self.bot.say("Member: {} is now registered with this bot and BANNED.".format(user.mention))
    
    @commands.command(pass_context=True)
    @commands.check(checks.is_admin)
    async def userunban(self, ctx, user: User):
        """
        Ban a user from the bot (ADMIN ONLY)
        """
        snowflake = user.id
        mysql.check_for_user(snowflake)

        soak_status = mysql.check_soakme(snowflake)
        if soak_status is None:
            await self.bot.say("Member: {} is not registered with this bot. The member will now be registered and marked as UNBANNED".format(user.mention))
            mysql.check_soakme(snowflake)
            mysql.set_soakme(snowflake, 0)
            await self.bot.say("Member: {} is now registered with this bot and UNBANNED.".format(user.mention))
        elif soak_status == 2:
            await self.bot.say("Member: {} is already UNBANNED.".format(user.mention))
        else:
            mysql.set_soakme(snowflake, 0)
            await self.bot.say("Member: {} is now marked as UNBANNED.".format(user.mention))
    
    @commands.command(pass_context=True)
    @commands.check(checks.is_admin)
    async def checkuserban(self, ctx, user: User):
        """
        Check if a user is banned from the bot (ADMIN ONLY)
        """
        snowflake = user.id
        mysql.check_for_user(snowflake)

        enable = mysql.check_soakme(snowflake)
        if enable != 2:
            await self.bot.say("User is not banned! :white_check_mark:")
        else:
            await self.bot.say("User is banned! :no_entry_sign:")

def setup(bot):
    bot.add_cog(Server(bot))
