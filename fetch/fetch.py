import discord
from discord.ext import commands


class Fetch:
    """Fetching stuff"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def fetch(self, user: discord.Member, *, stuff):
        """Fetches stuff to user"""

        await self.bot.say("Have your " + stuff + ", " + user.mention)


def setup(bot):
    bot.add_cog(Fetch(bot))
