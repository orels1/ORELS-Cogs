import discord
from discord.ext import commands
import aiohttp
import re
import logging


log = logging.getLogger('red.steam')


class Steam:
    """Steam and SteamSpy related commands"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, name='sales', aliases=['owners'])
    async def gamesales(self, ctx, *, game):
        """Shows estimated amount of owners for the game"""

        # gets info from SteamSpy
        async def gatherGameInfo(appid):

            # get the game info by appid from SteamSpy (c)
            # ratelimited for 4 req/s
            # TODO: add local caching
            url = "http://steamspy.com/api.php?"
            url += "request=appdetails"
            url += "&"
            url += "appid=" + str(appid)

            async with aiohttp.get(url) as r:
                data = await r.json()
            if "error" not in data.keys():
                return data
            else:
                return None

        # result refiner process
        async def refineResults(result):
            result = result[0:5]

            message = "Found a lot of results, please choose one (type a number from the list): \n \n"

            for game in enumerate(result):
                message += str(game[0] + 1) + ". " + str(game[1]['name']) + "\n"

            await self.bot.say(message)

            # number checker
            def is_number(s):
                try:
                    int(s)
                    return True
                except ValueError:
                    return False

            answer = await self.bot.wait_for_message(timeout=15, author=ctx.message.author)

            if answer:
                if is_number(answer.content.strip()) and int(answer.content.strip()) in range(1, 6):
                    return(result[int(answer.content.strip()) - 1]['appid'])
                else:
                    await self.bot.say("Please enter just a number next time :(")
                    return None

        # get the appIds list first
        url = "http://api.steampowered.com/ISteamApps/GetAppList/v0002/"

        # we will store our stuff in here
        result = []
        async with aiohttp.get(url) as r:
            data = await r.json()
        if "error" not in data.keys():

            # check for romanian numbers
            testR = re.compile('\s[vVxX](\W|$)',).search(game)
            if testR is not None:
                game = game[:testR.start() + 1] + '\s' + game[testR.start() + 1:]

            # create regexp for matching
            test = re.compile('.*' + '.*'.join(game.split()) + '.*', re.I)

            # Build the data into a nice table and send
            for d in data['applist']['apps']:
                if test.search(d['name'].lower()) is not None:
                    result.append({
                        "appid": d['appid'],
                        "name": d['name']
                    })

            gameResult = None
            appId = None
            if len(result) == 0:
                # no games were found
                return await self.bot.say('There are no games like that one :\'(')
            elif len(result) == 1:
                # only one game matched
                appId = result[0]['appid']
                gameResult = await gatherGameInfo(appId)
            else:
                # multiple matches
                gPos = None
                try:
                    # searches for the exact game name (case-insensitive)
                    gPos = next(i for i, g in enumerate(result) if g['name'].lower() == game.lower())
                except ValueError:
                    gPos = None
                except StopIteration:
                    gPos = None

                if gPos is not None:
                    # if found exact game name in the list of matches
                    appId = result[gPos]['appid']
                    # SteamSpy API
                    apiReturn = await gatherGameInfo(appId)
                    # if SteamSpy returned data
                    if apiReturn is not None:
                        gameResult = apiReturn
                else:
                    # let the user choose from the list of matches
                    appId = await refineResults(result)
                    # SteamSpy API
                    apiReturn = await gatherGameInfo(appId)
                    # if SteamSpy returned data
                    if apiReturn is not None:
                        gameResult = apiReturn

            if gameResult is not None:
                # build embed
                em = discord.Embed(title=gameResult['name'],
                                   url='http://store.steampowered.com/app/' + str(appId),
                                   colour=0x2F668D)
                em.set_thumbnail(url='http://cdn.akamai.steamstatic.com/steam/apps/' + str(appId) + '/header.jpg')
                em.set_author(name='Steam Spy',
                              url='http://steamspy.com/app/' + str(appId),
                              icon_url='https://pbs.twimg.com/profile_images/624266818891423744/opyF6mM5_400x400.png')
                em.add_field(name='Owners',
                             value=str('{0:,}'.format(gameResult['owners'])) + ' ±' + str('{0:,}'.format(gameResult['owners_variance'])),
                             inline=True)
                em.add_field(name='Players in last 2 weeks',
                             value=str('{0:,}'.format(gameResult['players_2weeks'])) + ' ±' + str('{0:,}'.format(gameResult['players_2weeks_variance'])),
                             inline=True)
                em.add_field(name='Peak in 24 hours',
                             value=str('{0:,}'.format(gameResult['ccu'])),
                             inline=True)
                em.set_footer(text='<3 SteamSpy')

                # send embed
                await self.bot.send_message(ctx.message.channel, embed=em)
            else:
                # something went wrong
                await self.bot.say('Something went wrong with SteamSpy')
        else:
            await self.bot.say('Something went wrong with Steam')

    @commands.command(pass_context=True, name='steam')
    async def steamgame(self, ctx, *, game):
        """Gets the link to a game on Steam"""

        # result refiner process
        async def refineResults(result):
            result = result[0:5]

            message = "Found a lot of results, please choose one (type a number from the list): \n \n"

            for game in enumerate(result):
                message += str(game[0] + 1) + ". " + str(game[1]['name']) + "\n"

            await self.bot.say(message)

            # number checker
            def is_number(s):
                try:
                    int(s)
                    return True
                except ValueError:
                    return False

            answer = await self.bot.wait_for_message(timeout=15, author=ctx.message.author)

            if answer:
                if is_number(answer.content.strip()) and int(answer.content.strip()) in range(1, 6):
                    await self.bot.say("http://store.steampowered.com/app/" +
                                       str(result[int(answer.content.strip()) - 1]['appid']))
                else:
                    await self.bot.say("Please enter just a number next time :(")

        # get the appIds list first
        url = "http://api.steampowered.com/ISteamApps/GetAppList/v0002/"
        # we will store our stuff in here
        result = []
        async with aiohttp.get(url) as r:
            data = await r.json()
        if "error" not in data.keys():

            # check for romanian numbers
            testR = re.compile('\s[vVxX](\W|$)').search(game)
            if testR is not None:
                game = game[:testR.start() + 1] + '\s' + game[testR.start() + 1:]

            # create regexp for matching
            test = re.compile('.*' + '.*'.join(game.split()) + '.*', re.I)

            # Build the data into a nice table and send
            for d in data['applist']['apps']:
                if test.search(d['name'].lower()) is not None:
                    result.append({
                        "appid": d['appid'],
                        "name": d['name']
                    })
            if len(result) == 0:
                return await self.bot.say('There are no games like that one :\'(')
            elif len(result) == 1 or result[0]['name'] == game:
                await self.bot.say("http://store.steampowered.com/app/" +
                                   str(result[0]['appid']))
            else:
                await refineResults(result)
        else:
            await self.bot.say(data["error"])


def setup(bot):
    n = Steam(bot)
    bot.add_cog(n)
