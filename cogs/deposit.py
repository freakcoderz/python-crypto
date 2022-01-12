import discord, json, requests
from discord.ext import commands
from utils import parsing, mysql_module

mysql = mysql_module.Mysql()

class Deposit:
    def __init__(self, bot):
        self.bot = bot
        config = parsing.parse_json('config.json')
        self.currency_symbol = config["currency_symbol"]  
        self.stakeflake = config["stake_bal"]
        self.treasurer = config["treasurer"]
        self.donate = config["donation"]
        self.game_id = config["game_bal"]
        self.coin_name = config["currency_name"]
        self.bot_name = config["description"]
        self.explorer = config["explorer_url"]

        #parse the embed section of the config file
        embed_config = parsing.parse_json('config.json')["embed_msg"]
        self.thumb_embed = embed_config["thumb_embed_url"]
        self.footer_text = embed_config["footer_msg_text"]
        self.embed_color = int(embed_config["color"], 16)

    @commands.command(pass_context=True)
    async def deposit(self, ctx):
        #"""Show Your Deposit Address on this Bot. Use the address to send coins to your account on this Bot."""
        #user = ctx.message.author
        #snowflake = ctx.message.author.id
        #balance = mysql.get_balance(snowflake, check_update=True)
        #balance_unconfirmed = mysql.get_balance(snowflake, check_unconfirmed = True)
        # Check if user exists in db
        #mysql.check_for_user(user.id)
        #user_addy = mysql.get_address(user.id)
        #embed=discord.Embed(title="You requested your **Deposit Address**", color=self.embed_color)
        embed=discord.Embed(title="Deposits are disabled", color=self.embed_color)
        #embed.set_author(name="{}".format(self.bot_name))
        #embed.set_thumbnail(url="http://{}".format(self.thumb_embed))
        #embed.add_field(name="User", value="{}".format(user), inline=False)
        #embed.add_field(name="Deposit Address", value="{}".format(user_addy), inline=False)
        #embed.add_field(name="Balance", value="{:.8f} {}".format(round(float(balance), 8),self.currency_symbol))
        #if float(balance_unconfirmed) != 0.0:
            #embed.add_field(name="Unconfirmed Deposits", value="{:.8f} {}".format(round(float(balance_unconfirmed), 8),self.currency_symbol))
        #embed.add_field(name="Deposit Transactions", value="Type $dlist for a list of your deposits.")
        #embed.add_field(name="Mobile Deposit", value="Type $mobile for your deposit address formatted for mobile.")
        #embed.set_footer(text=self.footer_text)
        #try:
            #await self.bot.send_message(ctx.message.author, embed=embed)
        #except discord.HTTPException:
            #await self.bot.say("I need the `Embed links` permission to send this")

        #if ctx.message.server is not None:
            #await self.bot.say("{}, I PMed you your **Deposit Address**! Make sure to double check that it is from me!".format(user.mention))

    #@commands.command(pass_context=True)
    #async def mobile(self, ctx):
        #"""Show Your Deposit Address on this Bot. Use the address to send coins to your account on this Bot. Formatted for easy copying on Mobile."""
        #user = ctx.message.author
        #snowflake = ctx.message.author.id
        # Check if user exists in db
        # mysql.check_for_user(user.id)
        #if mysql.check_for_user(snowflake) is None:
            #return
        #user_addy = mysql.get_address(user.id)

        #await self.bot.send_message(ctx.message.author, "Your {} ({}) Deposit Address: \n".format(self.coin_name, self.currency_symbol))
        #await self.bot.send_message(ctx.message.author, "**{}**".format(user_addy))

        #if ctx.message.server is not None:
            #await self.bot.say("{}, I PMed you your **Deposit Address**! Make sure to double check that it is from me!".format(user.mention))

    @commands.command(pass_context=True)
    async def dlist(self, ctx):
        """Show a list of your Deposits on this Bot. TXID, Amount, and Deposit Status are displayed to easily track deposits."""
        user = ctx.message.author
        # only allow this message to be sent privatly for privacy - send a message to the user in the server.    
        if ctx.message.server is not None:
            await self.bot.say("{}, I PMed you your **Deposit List**! Make sure to double check that it is from me!".format(user.mention))
        # begin sending pm transaction list to user
        await self.bot.send_message(ctx.message.author, "{} You requested Your **{} ({}) Deposits**: \n".format(user.mention, self.coin_name, self.currency_symbol))
        # Check if user exists in db
        if mysql.check_for_user(user.id) is None:
            await self.bot.say("User is not found in the database")
            return
        user_addy = mysql.get_address(user.id)
        await self.bot.send_message(ctx.message.author, "Deposit Address: **{}**".format(user_addy))
        # Get the list of deposit txns by user.id transactions
        conf_txns = mysql.get_deposit_list_byuser(user.id)
        await self.bot.send_message(ctx.message.author, "Number of Deposits: **{}**".format(len(conf_txns)))
        # List the transactions
        for txns in conf_txns:
            dep_amount = mysql.get_deposit_amount(txns)
            dep_status = mysql.get_transaction_status_by_txid(txns)
            #await self.bot.send_message(ctx.message.author, "TXID: <https://{}{}>".format(self.explorer, str(txns)))
            await self.bot.send_message(ctx.message.author, "Deposit amount {:.8f} {}".format(float(dep_amount), "Deposit Status {}".format(dep_status), self.currency_symbol))
            #await self.bot.send_message(ctx.message.author, "Deposit Status {}".format(dep_status))


def setup(bot):
    bot.add_cog(Deposit(bot))