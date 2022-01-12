import discord
from discord.ext import commands
from utils import rpc_module, mysql_module, parsing, checks

#result_set = database response with parameters from query
#db_bal = nomenclature for result_set["balance"]
#snowflake = snowflake from message context, identical to user in database
#wallet_bal = nomenclature for wallet reponse

rpc = rpc_module.Rpc()
mysql = mysql_module.Mysql()


class Txlist:

    def __init__(self, bot):
        self.bot = bot

        #parse the config file
        config = parsing.parse_json('config.json')
        self.currency_symbol = config["currency_symbol"]   
        self.stakeflake = config["stake_bal"]
        self.treasurer = config["treasurer"]
        self.donate = config["donation"]
        self.game_id = config["game_bal"]
        self.coin_name = config["currency_name"]
        self.bot_name = config["description"]

        #parse the embed section of the config file
        embed_config = parsing.parse_json('config.json')["embed_msg"]
        self.thumb_embed = embed_config["thumb_embed_url"]
        self.footer_text = embed_config["footer_msg_text"]
        self.embed_color = int(embed_config["color"], 16)

    async def do_fee_embed(self, name, db_bal, db_bal_unconfirmed, stake_total):
        # Simple embed function for displaying username and balance
        embed=discord.Embed(title="You requested the **Fee Balance**", color=self.embed_color)
        embed.set_author(name="{} ADMIN".format(self.bot_name))
        embed.add_field(name="User", value=name, inline=False)
        embed.add_field(name="Balance", value="{:.8f} {}".format(round(float(db_bal), 8),self.currency_symbol))
        embed.set_thumbnail(url="http://{}".format(self.thumb_embed))
        if float(db_bal_unconfirmed) != 0.0:
            embed.add_field(name="Unconfirmed Fee Deposits", value="{:.8f} {}".format(round(float(db_bal_unconfirmed), 8),self.currency_symbol))
        if float(stake_total) != 0.0:
            embed.add_field(name="Your Total Staking Rewards", value="{:.8f} {}".format(round(float(stake_total), 8),self.currency_symbol))
        embed.set_footer(text=self.footer_text)
        try:
            await self.bot.say(embed=embed)
        except discord.HTTPException:
            await self.bot.say("I need the `Embed links` permission to send this")

    async def do_donate_embed(self, name, db_bal, db_bal_unconfirmed, stake_total):
        # Simple embed function for displaying username and balance
        embed=discord.Embed(title="You requested the **Donate Balance**", color=self.embed_color)
        embed.set_author(name="{} ADMIN".format(self.bot_name))
        embed.add_field(name="User", value=name, inline=False)
        embed.add_field(name="Balance", value="{:.8f} {}".format(round(float(db_bal), 8),self.currency_symbol))
        embed.set_thumbnail(url="http://{}".format(self.thumb_embed))
        if float(db_bal_unconfirmed) != 0.0:
            embed.add_field(name="Unconfirmed Deposits", value="{:.8f} {}".format(round(float(db_bal_unconfirmed), 8),self.currency_symbol))
        if float(stake_total) != 0.0:
            embed.add_field(name="Your Total Staking Rewards", value="{:.8f} {}".format(round(float(stake_total), 8),self.currency_symbol))
        embed.set_footer(text=self.footer_text)
        try:
            await self.bot.say(embed=embed)
        except discord.HTTPException:
            await self.bot.say("I need the `Embed links` permission to send this")

    async def do_all_embed(self, name, address, request, db_bal, db_bal_unconfirmed, stake_total):
        # Simple embed function for displaying username and balance
        embed=discord.Embed(title="You requested the **{}**".format(request), color=self.embed_color)
        embed.set_author(name="{} ADMIN".format(self.bot_name))
        embed.add_field(name="User", value="{} {}".format(self.coin_name, name), inline=False)
        embed.add_field(name="Address", value=str(address), inline=False)
        embed.add_field(name="Balance", value="{:.8f} {}".format(round(float(db_bal), 8),self.currency_symbol))
        embed.set_thumbnail(url="http://{}".format(self.thumb_embed))
        if float(db_bal_unconfirmed) != 0.0:
            embed.add_field(name="Unconfirmed Deposits", value="{:.8f} {}".format(round(float(db_bal_unconfirmed), 8),self.currency_symbol))
        if float(stake_total) != 0.0:
            embed.add_field(name="Your Total Staking Rewards", value="{:.8f} {}".format(round(float(stake_total), 8),self.currency_symbol))
        embed.set_footer(text=self.footer_text)
        try:
            await self.bot.say(embed=embed)
        except discord.HTTPException:
            await self.bot.say("I need the `Embed links` permission to send this")


    @commands.command(hidden=True)
    @commands.check(checks.is_owner)
    async def fees(self):
        """Display your balance"""
        # Set important variables
        snowflake = str(self.treasurer)
        #await self.bot.say("Staking account snowflake: {}".format(snowflake))
        name = str("Treasury Account - Withdrawl and Staking Fees")

        # Check if user exists in db
        #await self.bot.say("Checking for updated mining balance")
        #mysql.check_for_updated_mining_balance()
        #await self.bot.say("Checking if staking user exists")
        mysql.get_staking_user(snowflake)

        #if you call get_balance with the snowflake equal to the tresury account
        #await self.bot.say("Checking balance")
        balance = mysql.get_balance(snowflake, check_update=True)

        #await self.bot.say("Checking unconfirmed staking balance")
        balance_unconfirmed = mysql.get_balance(snowflake, check_unconfirmed = True)

        # get the users staking rewards
        stakes =  mysql.get_tip_amounts_from_id(self.stakeflake, snowflake)

        # Execute and return SQL Query
        await self.do_fee_embed(name, balance, balance_unconfirmed, sum(stakes))

    @commands.command(hidden=True)
    @commands.check(checks.is_owner)
    async def donations(self):
        # Set important variables
        snowflake = str(self.donate)
        #await self.bot.say("Staking account snowflake: {}".format(snowflake))
        name = str("Donation Account")

        # Check if user exists in db
        #await self.bot.say("Checking for updated mining balance")
        #mysql.check_for_updated_mining_balance()
        #await self.bot.say("Checking if staking user exists")
        mysql.get_staking_user(snowflake)

        #if you call get_balance with the snowflake equal to the staking account it will initialize the check for mined transactions
        #the mined transactions are added to the staking account
        #await self.bot.say("Checking balance")
        balance = mysql.get_balance(snowflake, check_update=True)

        #await self.bot.say("Checking unconfirmed staking balance")
        balance_unconfirmed = mysql.get_balance(snowflake, check_unconfirmed = True)

        stakes =  mysql.get_tip_amounts_from_id(self.stakeflake, snowflake)

        # Execute and return SQL Query
        await self.do_donate_embed(name, balance, balance_unconfirmed, sum(stakes))

    @commands.command(hidden=True)
    @commands.check(checks.is_admin)
    async def gamebal(self):
        # Set important variables
        snowflake = str(self.game_id)
        #await self.bot.say("Staking account snowflake: {}".format(snowflake))
        name = str("Game Account")
        request = str("Game Balance")

        # Check if user exists in db
        #await self.bot.say("Checking for updated mining balance")
        #mysql.check_for_updated_mining_balance()
        #await self.bot.say("Checking if staking user exists")
        mysql.get_staking_user(snowflake)

        #get user addres
        address = mysql.get_address(snowflake)

        #if you call get_balance with the snowflake equal to the staking account it will initialize the check for mined transactions
        #the mined transactions are added to the staking account
        #await self.bot.say("Checking balance")
        balance = mysql.get_balance(snowflake, check_update=True)

        #await self.bot.say("Checking unconfirmed staking balance")
        balance_unconfirmed = mysql.get_balance(snowflake, check_unconfirmed = True)

        stakes =  mysql.get_tip_amounts_from_id(self.stakeflake, snowflake)

        # Execute and return SQL Query
        await self.do_all_embed(name, address, request, balance, balance_unconfirmed, sum(stakes))

def setup(bot):
    bot.add_cog(Txlist(bot))
