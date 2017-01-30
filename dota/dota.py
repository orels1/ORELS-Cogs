import discord
from discord.ext import commands
from .utils.dataIO import fileIO
import os
import aiohttp
import html

# Check if BeautifulSoup4 is installed
try:
    from bs4 import BeautifulSoup
    soupAvailable = True
except:
    soupAvailable = False

# Check if Dota2py is installed
try:
    from dota2py import api
    dotaAvailable = True
except:
    dotaAvailable = False

# Check if tabulate is installed
try:
    from tabulate import tabulate
    tabulateAvailable = True
except:
    tabulateAvailable = False

class Dota:
    """Dota 2 Red Cog"""

    def __init__(self, bot):
        self.bot = bot
        self.dota_settings = fileIO("data/dota/settings.json", "load")

        # Check for key either in settings or in ENV
        if "key" in self.dota_settings.keys() and self.dota_settings["key"] != "":

            # If exists in setting and is set
            api.set_api_key(self.dota_settings["key"])
            self.key = True

        elif os.environ.get("DOTA2_API_KEY") is not None:

            # If exists in env vars and is set
            api.set_api_key(os.environ.get("DOTA2_API_KEY"))
            self.key = True

        else:
            self.key = False


    @commands.group(pass_context = True)
    async def dota(self, ctx):
        """Returns various data for dota players"""

        if ctx.invoked_subcommand is None:
            await self.bot.say("Type help dota for info.")

    @dota.command(name = 'setkey', pass_context = True)
    async def setkey(self, ctx, key):
        """Sets the Dota 2 Wep API key (PM ONLY)"""

        # Perform the PM check
        if ctx.message.channel.is_private:

            self.dota_settings["key"] = key.strip()
            fileIO("data/dota/settings.json", "save", self.dota_settings)

            # Set the client's API key
            api.set_api_key(self.dota_settings["key"])

            # Change the current key status
            self.key = True

            await self.bot.say("Key saved and applied")
        else:
            await self.bot.say("Please run this command in PM")

    @dota.command(name = 'online', pass_context = True)
    async def online(self, ctx):
        """Returns current amount of players"""

        # Build an url
        url = "https://steamdb.info/app/570/graphs/"

        async with aiohttp.get(url) as response:
            soupObject = BeautifulSoup(await response.text(), "html.parser")

        # Parse the data and send it
        try:
            online = soupObject.find(class_='home-stats').find('li').find('strong').get_text()
            await self.bot.say(online + ' players are playing this game at the moment')
        except:
            await self.bot.say("Couldn't load amount of players. No one is playing this game anymore or there's an error.")

    @dota.command(name = 'hero', pass_context = True)
    async def hero(self, ctx, *, heroReq):
        """Return requested hero's stats"""

        # Gamepedia hero attributes api url (it's static)
        url = "http://dota2.gamepedia.com/api.php?action=parse&format=json&pageid=178308"

        try:
            async with aiohttp.get(url, headers={"User-Agent": "Red-DiscordBot"}) as response:
                data = await response.json()

                unescaped = html.unescape(data["parse"]["text"]["*"])

                soupObject = BeautifulSoup(unescaped, "html.parser")

                #print(soupObject)

                rows = soupObject.find(class_='wikitable sortable').find_all('tr')

                # find our hero
                heroIndex = None

                for row in enumerate(rows[1:]):
                    heroName = row[1].find_all('td')[0].getText()[:-2]
                    if heroReq.lower() in heroName.lower():
                        # found it!
                        heroIndex = row[0] + 1

                if not heroIndex:
                    return await self.bot.say('Couldn\'t find requested hero')

                heroStats = rows[heroIndex].find_all('td')

                # dotabuff base url
                baseUrl = 'https://www.dotabuff.com/heroes'

                # collect hero info
                hero = {
                    'name': heroStats[0].getText()[:-2],
                    'img': heroStats[0].find('img')['src'],
                    'url': baseUrl + heroStats[0].find('a')['href'].lower().replace('_','-'),
                    'attribute': heroStats[1].find('a')['title'],
                    'str': [heroStats[2].getText()[1:-1], heroStats[3].getText()[1:-1]], # stripping the text with [1:-1]
                    'agi': [heroStats[4].getText()[1:-1], heroStats[5].getText()[1:-1]],
                    'int': [heroStats[6].getText()[1:-1], heroStats[7].getText()[1:-1]],
                    'ms': heroStats[11].getText()[1:-1],
                    'armor': heroStats[12].getText()[1:-1],
                    'attack': [heroStats[13].getText()[1:-1],heroStats[14].getText()[1:-1]],
                    'range': heroStats[15].getText()[1:-1],
                    'vision': [heroStats[19].getText()[1:-1],heroStats[20].getText()[1:-1]],
                    'regen': heroStats[23].getText()[1:-1]
                }

                # set embed color based on primary attribute
                if hero['attribute'] == 'Strength':
                    hero['color'] = 0xF24A0B
                elif hero['attribute'] == 'Agility':
                    hero['color'] = 0x55C156
                else:
                    hero['color'] = 0x2F668D


                # build embed
                em = discord.Embed(title='{} ({})'.format(hero['name'], hero['attribute']),
                                   url=hero['url'],
                                   colour=hero['color'])
                em.set_thumbnail(url=hero['img'])
                em.add_field(name='Strength',
                             value='{} (+{}/lvl)'.format(hero['str'][0], hero['str'][1]),
                             inline=True)
                em.add_field(name='Agility',
                             value='{} (+{}/lvl)'.format(hero['agi'][0], hero['agi'][1]),
                             inline=True)
                em.add_field(name='Intelligence',
                             value='{} (+{}/lvl)'.format(hero['int'][0], hero['int'][1]),
                             inline=True)
                em.add_field(name='Movement speed',
                             value=hero['ms'],
                             inline=True)
                em.add_field(name='Armor',
                             value=hero['armor'],
                             inline=True)
                em.add_field(name='Regen',
                             value=hero['regen'],
                             inline=True)
                em.add_field(name='Attack',
                             value='{}-{}'.format(hero['attack'][0],hero['attack'][1]),
                             inline=True)
                em.add_field(name='Range',
                             value=hero['range'],
                             inline=True)
                em.add_field(name='Vision (day/night)',
                             value='{}/{}'.format(hero['vision'][0],hero['vision'][1]),
                             inline=True)
                em.set_footer(text='<3 Dota cog, Gamepedia & Dotabuff')

                # send embed
                await self.bot.send_message(ctx.message.channel, embed=em)
        except:
            await self.bot.say('Couldn\'t get info from Gamepedia API :(')

    @dota.command(name = 'build', pass_context = True)
    async def build(self, ctx, *, hero):
        """Gets most popular skillbuild for a hero"""

        # Build an url
        url = "http://www.dotabuff.com/heroes/" + hero.lower().replace(" ", "-")

        async with aiohttp.get(url, headers = {"User-Agent": "Red-DiscordBot"}) as response:
            soupObject = BeautifulSoup(await response.text(), "html.parser")

        # "build" will contain a final table
        # "headers" will contain table headers with lvl numbers
        build = []
        headers = ""

        try:
            skillSoup = soupObject.find(class_='skill-choices')

            # Generate skill tree
            for skill in enumerate(skillSoup.find_all(class_='skill')):

                # Get skill names for the first row
                build.append([skill[1].find(class_='line').find(class_='icon').find('img').get('alt')])

                # Generate build order
                for entry in enumerate(skill[1].find(class_='line').find_all(class_='entry')):
                    if "choice" in entry[1].get("class"):
                        build[skill[0]].append("X")
                    else:
                        build[skill[0]].append(" ")

            # Get a part of the table
            def getPartialTable(table, start, end):
                tables = []
                for row in enumerate(table):
                    if start == 0:
                        result = []
                    else:
                        result = [table[row[0]][0]]
                    result[1:] = row[1][start:end]
                    tables.append(result)
                return tables

            # Generate 2 messages (for a splitted table)
            # TODO: Convert into one "for" cycle
            message = "The most popular build **at the moment**, according to Dotabuff:\n\n"
            message += "```"
            headers = ["Skill/Lvl"]
            headers[len(headers):] = range(1,7)
            message += tabulate(getPartialTable(build,1,7), headers=headers, tablefmt="fancy_grid")
            message += "```\n"

            message += "```"
            headers = ["Skill/Lvl"]
            headers[len(headers):] = range(7,13)
            message += tabulate(getPartialTable(build,7,13), headers=headers, tablefmt="fancy_grid")
            message += "```\n"

            # Send first part
            await self.bot.say(message)

            message = "```"
            headers = ["Skill/Lvl"]
            headers[len(headers):] = range(13,19)
            message += tabulate(getPartialTable(build,13,19), headers=headers, tablefmt="fancy_grid")
            message += "```\n"

            # Send second part
            await self.bot.say(message)
        except:

            # Nothing can be done
            await self.bot.say("Error parsing Dotabuff, maybe try again later")

    @dota.command(name = 'items', pass_context = True)
    async def items(self, ctx, *, hero):
        """Gets the most popular items for a hero"""

        # Build an url
        url = "http://www.dotabuff.com/heroes/" + hero.lower().replace(" ", "-")

        async with aiohttp.get(url, headers = {"User-Agent": "Red-DiscordBot"}) as response:
            soupObject = BeautifulSoup(await response.text(), "html.parser")

        # Get the needed data fron the page
        # TODO: Add try-except block
        items = soupObject.find_all("section")[3].find("tbody").find_all("tr")

        # "build" will contain a final table
        build = []

        # Generate the buld from data
        for item in items:
            build.append(
                [
                    item.find_all("td")[1].find("a").get_text(),
                    item.find_all("td")[2].get_text(),
                    item.find_all("td")[4].get_text()
                ]
            )

        # Compose the message
        message = "The most popular items **at the moment**, according to Dotabuff:\n\n```"
        message += tabulate(build, headers=["Item", "Matches", "Winrate"], tablefmt="fancy_grid")
        message += "```"

        await self.bot.say(message)

    def _build_match_embed(self, match):
        # extract additional data
        winner = ''
        color = 0xF24A0B
        if match['data']['radiant_win']:
            winner = 'radiant won'
            color = 0x55C156
        else:
            winner = 'dire won'

        # build embed
        em = discord.Embed(title='Match {} ({})'.format(match['id'], winner),
                           url='http://www.dotabuff.com/matches/{}'.format(match['id']),
                           colour=color)
        # em.set_thumbnail(url='some_url')

        # add radiant team
        radiant_totals = [0,0,0]
        em.add_field(name='Radiant team', value='v==== (K/D/A) ====v', inline=False)
        for radiant_player in match['teams']['radiant']:
            em.add_field(name='{}'.format(radiant_player['name']),
                         value='{}/{}/{}'.format(radiant_player['kills'],
                                                 radiant_player['deaths'],
                                                 radiant_player['assists']),
                         inline=True)
            # upate totals
            radiant_totals[0] += int(radiant_player['kills'])
            radiant_totals[1] += int(radiant_player['deaths'])
            radiant_totals[2] += int(radiant_player['assists'])
        # add totals
        em.add_field(name='Total stats',
                     value='{}/{}/{}'.format(radiant_totals[0], radiant_totals[1], radiant_totals[2]),
                     inline=True)

        # add dire team
        dire_totals = [0,0,0]
        em.add_field(name='Dire team', value='v==== (K/D/A) ====v', inline=False)
        for dire_player in match['teams']['dire']:
            em.add_field(name='{}'.format(dire_player['name']),
                         value='{}/{}/{}'.format(dire_player['kills'],
                                                 dire_player['deaths'],
                                                 dire_player['assists']),
                         inline=True)
            # upate totals
            dire_totals[0] += int(radiant_player['kills'])
            dire_totals[1] += int(radiant_player['deaths'])
            dire_totals[2] += int(radiant_player['assists'])
        # add totals
        em.add_field(name='Total stats',
                     value='{}/{}/{}'.format(dire_totals[0], dire_totals[1], dire_totals[2]),
                     inline=True)

        em.set_footer(text='<3 Dota cog & Dotabuff')

        return em

    @dota.command(name = 'recent', pass_context = True)
    async def recent(self, ctx, player):
        """Gets the link to player's latest match"""

        # Check it there is an api key set
        if not self.key:
            await self.bot.say("Please set the dota 2 api key using [p]dota setkey command")
            raise RuntimeError("Please set the dota 2 api key using [p]dota setkey command")

        # Required to check if user provided the ID or not
        def is_number(s):
            try:
                int(s)
                return True
            except ValueError:
                return False

        # Check if user provided the ID
        if is_number(player.strip()):

            # if he did - assign as-is
            account_id = player.strip()
        else:
            # if he did not - get the id from the vanity name
            account_id = api.get_steam_id(player)["response"]

            # Check if the result was correcct
            if (int(account_id["success"]) > 1):
                await self.bot.say("Player not found :(")
            else:
                account_id = account_id["steamid"]

        try:
            # Get the data from Dota API
            matches = api.get_match_history(account_id=account_id)["result"]["matches"]
            match = api.get_match_details(matches[0]["match_id"])
            heroes = api.get_heroes()

            # Operation was a success
            dotaServes = True
        except:

            # Well... if anything fails...
            dotaServes = False
            print('Dota servers SO BROKEN!')

        # Proceed to data parsing
        if dotaServes:

            # relink for ease of use
            match = match["result"]

            # Create a proper heroes list
            heroes = heroes["result"]["heroes"]
            def build_dict(seq, key):
                return dict((d[key], dict(d, index=index)) for (index, d) in enumerate(seq))
            heroes = build_dict(heroes, "id")

            # Create a list of played heroes
            played_heroes = []
            for player in enumerate(match["players"]):
                played_heroes.append(heroes[player[1]["hero_id"]]["localized_name"])

            # form teams
            teams = {
                'radiant': [],
                'dire': []
            }
            for i in range(0,5):
                teams['radiant'].append({
                    'name': played_heroes[i],
                    'kills': str(match["players"][i]["kills"]),
                    'deaths': str(match["players"][i]["deaths"]),
                    'assists': str(match["players"][i]["assists"])
                    })
                teams['dire'].append({
                    'name': played_heroes[5+i],
                    'kills': str(match["players"][5+i]["kills"]),
                    'deaths': str(match["players"][5+i]["deaths"]),
                    'assists': str(match["players"][5+i]["assists"])
                    })

            # Reassign match info for ease of use
            matchData = {
                'id': match['match_seq_num'],
                'teams': teams,
                'data': match
                }

            await self.bot.send_message(ctx.message.channel, embed=self._build_match_embed(matchData))
        else:
            await self.bot.say('Oops.. Something is wrong with Dota2 servers, try again later!')

    @dota.command(name = 'match', pass_context = True)
    async def match(self, ctx, matchId):
        """Gets the match results by id"""

        # Check it there is an api key set
        if not self.key:
            await self.bot.say("Please set the dota 2 api key using [p]dota setkey command")
            raise RuntimeError("Please set the dota 2 api key using [p]dota setkey command")

        # Required to check if user provided the ID or not
        def is_number(s):
            try:
                int(s)
                return True
            except ValueError:
                return False

        # Check if user provided the ID
        if not is_number(matchId.strip()):
            return self.bot.say('Please provide a numeric match id')

        # if he did - assign as-is
        match_id = matchId.strip()

        try:
            # Get the data from Dota API
            match = api.get_match_details(match_id)
            heroes = api.get_heroes()

            # Operation was a success
            dotaServes = True
        except:

            # Well... if anything fails...
            dotaServes = False
            print('Dota servers SO BROKEN!')

        # Proceed to data parsing
        if dotaServes:

            # relink for ease of use
            match = match["result"]

            # Create a proper heroes list
            heroes = heroes["result"]["heroes"]
            def build_dict(seq, key):
                return dict((d[key], dict(d, index=index)) for (index, d) in enumerate(seq))
            heroes = build_dict(heroes, "id")

            # Create a list of played heroes
            played_heroes = []
            for player in enumerate(match["players"]):
                played_heroes.append(heroes[player[1]["hero_id"]]["localized_name"])

            # form teams
            teams = {
                'radiant': [],
                'dire': []
            }
            for i in range(0,5):
                teams['radiant'].append({
                    'name': played_heroes[i],
                    'kills': str(match["players"][i]["kills"]),
                    'deaths': str(match["players"][i]["deaths"]),
                    'assists': str(match["players"][i]["assists"])
                    })
                teams['dire'].append({
                    'name': played_heroes[5+i],
                    'kills': str(match["players"][5+i]["kills"]),
                    'deaths': str(match["players"][5+i]["deaths"]),
                    'assists': str(match["players"][5+i]["assists"])
                    })

            # Reassign match info for ease of use
            matchData = {
                'id': match_id,
                'teams': teams,
                'data': match
                }

            await self.bot.send_message(ctx.message.channel, embed=self._build_match_embed(matchData))
        else:
            await self.bot.say('Oops.. Something is wrong with Dota2 servers, try again later!')
def check_folders():
    if not os.path.exists("data/dota"):
        print("Creating data/dota folder...")
        os.makedirs("data/dota")

def check_files():
    f = "data/dota/settings.json"
    if not fileIO(f, "check"):
        print("Creating empty settings.json...")
        fileIO(f, "save", {})

def setup(bot):
    if soupAvailable is False:
        raise RuntimeError("You don't have BeautifulSoup installed, run\n```pip3 install bs4```And try again")
        return
    if dotaAvailable is False:
        raise RuntimeError("You don't have dota2py installed, run\n```pip3 install dota2py```And try again")
        return
    if tabulateAvailable is False:
        raise RuntimeError("You don't have tabulate installed, run\n```pip3 install tabulate```And try again")
        return
    check_folders()
    check_files()
    bot.add_cog(Dota(bot))
