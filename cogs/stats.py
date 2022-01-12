import discord, os
from discord.ext import commands
from utils import checks, output
from aiohttp import ClientSession
import urllib.request
import json

class Stats:
    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot

    @commands.command()
    async def stats(self, amount=1):
        """
        Show stats about Aevo
        """
        #headers={"user-agent" : "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36"}
        #try:
            #async with ClientSession() as session:
                #async with session.get("https://api.coingecko.com/api/v3/coins/aevo", headers=headers) as response:
                    #responseRaw = await response.read()
                    #priceData = json.loads(responseRaw)
                    #btcPrice = priceData['market_data']['current_price']['btc']
                    #usdPrice = priceData['market_data']['current_price']['usd']
        embed = discord.Embed(color=0x00FF00)
        embed.set_author(name='Aevo Coin Information')
        embed.add_field(name="Price (USD)", value="😂")
        embed.add_field(name="Price (BTC)", value="🤣")
                        #embed.add_field(name="Volume (USD)", value="${}".format(priceData['market_data']['total_volume']['usd']))
                        #embed.add_field(name="Volume (BTC)", value="\u20bf{0:.9f}".format(priceData['market_data']['total_volume']['btc']))
                        #embed.add_field(name='\u200b',value='\u200b')
                        #embed.add_field(name="Price Change % 24h", value="{}%".format(priceData['market_data']['price_change_percentage_24h']))
                        #embed.add_field(name="Price Change % 7d", value="{}%".format(priceData['market_data']['price_change_percentage_7d']))
                        #embed.add_field(name="Masternode Required", value="42500 Aevo")
                        #embed.add_field(name="MN Cost (USD)", value="${:4.2f}".format(usdPrice*42500))
                        #embed.add_field(name="MN Cost (BTC)", value="\u20bf{:12.08f}".format(btcPrice*42500))
        await self.bot.say(embed=embed)
        #except:
            #output.info(":warning: Error fetching prices!")


def setup(bot):
    bot.add_cog(Stats(bot))
