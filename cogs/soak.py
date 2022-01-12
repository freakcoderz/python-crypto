import math
import discord
from discord.ext import commands
from utils import rpc_module, mysql_module, checks, parsing
import random

rpc = rpc_module.Rpc()
mysql = mysql_module.Mysql()


class Soak:
    def __init__(self, bot):
        self.bot = bot
        soak_config = parsing.parse_json('config.json')['soak']
        config = parsing.parse_json('config.json')         
        '''
        soak_max_recipients sets the max recipients for a soak. chosen randomly.
        soak_min_received sets the minimum possible soak received for a user.
        The number of soak recipients will be adjusted to fit these constraints
        if enabled via use_max_recipients and use_min_received
        '''
        self.soak_max_recipients = soak_config["soak_max_recipients"]
        self.use_max_recipients = soak_config["use_max_recipients"]
        self.soak_min_received = soak_config["soak_min_received"]
        self.use_min_received = soak_config["use_min_received"]
        self.soak_minimum = soak_config['min_amount']        
        self.currency_symbol = config["currency_symbol"] 
        self.prefix = config["prefix"]           

    @commands.command(pass_context=True)
    @commands.check(checks.allow_soak)
    async def soak(self, ctx, amount: float, role_id=""):
        """Tip all online users"""
        if self.use_max_recipients and self.soak_max_recipients == 0:
            await self.bot.say("**⚠WARNING Support is ending, withdraw funds!!⚠****:warning: max users for soak is set to 0! Talk to the config owner. :warning:**")
            return

        if amount < self.soak_minimum:
            await self.bot.say("**⚠WARNING Support is ending, withdraw funds!!⚠****:warning: Amount {:.8f} {} for soak is less than minimum {:.8f} {} required! :warning:**".format(float(amount), self.currency_symbol, float(self.soak_minimum), self.currency_symbol))
            return

        snowflake = ctx.message.author.id

        mysql.check_for_user(snowflake)
        balance = mysql.get_balance(snowflake, check_update=True)

        if float(balance) < amount:
            await self.bot.say("**⚠WARNING Support is ending, withdraw funds!!⚠**{} **:warning:You cannot soak more {} than you have!:warning:**".format(ctx.message.author.mention, self.currency_symbol))
            return

        users_list=[]
        if role_id=="" or role_id=="@everyone" or role_id=="@here" or role_id=="all":
            for user in ctx.message.server.members:
                if mysql.check_for_user(user.id) is not None:
                    if user.status == discord.Status.online or user.status == discord.Status.idle:
                        users_list.append(user)
        
        else:
            server_roles = ctx.message.server.roles
            role=[x for x in server_roles if x.mention==role_id]
            if len(role)==0:
                await self.bot.say("**⚠WARNING Support is ending, withdraw funds!!⚠**{}, This role does not exist! To tip a single user, use {}tip command instead.".format(ctx.message.author.mention,self.prefix))
                return
            else:
                for user in ctx.message.server.members:
                    if role[0] in user.roles:
                        if mysql.check_for_user(user.id) is not None:
                            if user.status == discord.Status.online or user.status == discord.Status.idle:
                                users_list.append(user)

        if role_id!="":
            online_users = [x for x in users_list]
        else:
            online_users = [x for x in users_list]

        if ctx.message.author in online_users:
            online_users.remove(ctx.message.author)

        online_users=[x for x in online_users if (x.status == discord.Status.online or user.status == discord.Status.idle and not x.bot)]
        
        for user in online_users:
            mysql.check_for_user(user.id)
            if mysql.check_soakme(user.id) != 1:
                online_users.remove(user)

        if self.use_max_recipients:
            len_receivers = min(len(online_users), self.soak_max_recipients)
        else:
            len_receivers = len(online_users)

        if self.use_min_received:
            len_receivers = min(len_receivers, amount / self.soak_min_received)

        if len_receivers == 0:
            return await self.bot.say("**⚠WARNING Support is ending, withdraw funds!!⚠**{}, you are all alone if you don't include bots! Trying soaking when people are online.".format(ctx.message.author.mention))
        
        amount_split = math.floor(float(amount) * 1e8 / len_receivers) / 1e8
        if amount_split == 0:
            await self.bot.say("**⚠WARNING Support is ending, withdraw funds!!⚠**{} **:warning:{:.8f} {} is not enough to split between {} users:warning:**".format(ctx.message.author.mention, float(amount), self.currency_symbol, len_receivers))
            return

        if role_id=="all" or role_id=="@everyone" or role_id=="@here":
            await self.bot.say("**⚠WARNING Support is ending, withdraw funds!!⚠**{} **Sorry, Soaking the {} role is not permitted.**".format(ctx.message.author.mention, role_id))
        else:
            receivers = []
            if role_id == "":
                for i in range(len_receivers):
                    user = random.choice(online_users)
                    receivers.append(user)
                    online_users.remove(user)
                    mysql.check_for_user(user.id)
                    mysql.add_tip(snowflake, user.id, amount_split)

                await self.bot.say("**⚠WARNING Support is ending, withdraw funds!!⚠**{} **Soaked {:.8f} {} on {} users** (Total {:.8f} {})".format(ctx.message.author.mention, float(amount_split), self.currency_symbol, len_receivers, float(amount), self.currency_symbol))
                users_soaked_msg = []
                idx = 0
                for users in receivers:
                    users_soaked_msg.append(users.mention)
                    idx += 1
                    if (len(users_soaked_msg) >= 50) or (idx == int(len_receivers)):
                        await self.bot.say("{}".format(' '.join(users_soaked_msg)))
                        del users_soaked_msg[:]
                        users_soaked_msg = []
            else:
                for i in range(len_receivers):
                    user = random.choice(online_users)
                    receivers.append(user)
                    online_users.remove(user)
                    mysql.check_for_user(user.id)
                    mysql.add_tip(snowflake, user.id, amount_split)

                long_soak_msg = "**⚠WARNING Support is ending, withdraw funds!!⚠**{} **Soaked {:.8f} {} on {} {} users** (Total {:.8f} {}) ".format(ctx.message.author.mention, float(amount_split), self.currency_symbol, len_receivers, role_id, float(amount), self.currency_symbol)

                #bot response:
                await self.bot.say(long_soak_msg)

                #parse into 25 username sized message chunks
                users_soaked_msg = []
                idx = 0
                for users in receivers:
                    users_soaked_msg.append(users.mention)
                    idx += 1
                    if (len(users_soaked_msg) >= 25) or (idx == int(len_receivers)):
                        await self.bot.say("{}".format(' '.join(users_soaked_msg)))
                        del users_soaked_msg[:]
                        users_soaked_msg = []


    @commands.command()
    @commands.check(checks.is_admin)
    async def soak_info(self):
        """Display min soak amount and maximum soak recipients"""
        if self.use_max_recipients:
            st_max_users = str(self.soak_max_recipients)
        else:
            st_max_users = "<disabled>"

        if self.use_min_received:
            st_min_received = str(self.soak_min_received)
        else:
            st_min_received = "<disabled>"
            
        await self.bot.say(":information_source: Soak info: max recipients {}, min amount receivable {} :information_source:".format(st_max_users, st_min_received))
        
    @commands.command(pass_context=True)
    async def soakme(self, ctx, enable: bool):
        """
        Allow/disallow other users from soaking you using 1 for on and 0 for off
        """
        snowflake = ctx.message.author.id
        mysql.check_for_user(snowflake)

        mysql.set_soakme(snowflake, int(enable))
        if enable:
            await self.bot.say("Ok! You will be soaked! :white_check_mark:")
        else:
            await self.bot.say("Ok! You will no longer be soaked! :no_entry_sign:")

def setup(bot):
    bot.add_cog(Soak(bot))