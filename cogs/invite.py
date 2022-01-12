from discord.ext import commands


class Invite:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def invite(self):
        """
        Get the bot's invite link
        """
        await self.bot.say("https://discordapp.com/api/oauth2/authorize?client_id=477114120299085854&permissions=8&scope=bot".format(self.bot.user.id))


def setup(bot):
    bot.add_cog(Invite(bot))
