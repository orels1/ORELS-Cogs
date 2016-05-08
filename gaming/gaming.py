import discord
from discord.ext import commands
from .utils.dataIO import fileIO
from .utils import checks
import asyncio
import textwrap
import os
import math
import aiohttp
from copy import copy


class Gaming:
    """Helps your gaming community"""

    def __init__(self, bot):
        self.bot = bot
        self.dbpath = "data/gaming/settings.json"
        self.db = fileIO(self.dbpath, "load")
                
        self.version = "1.0.0"
        self.update_type = "release"
        self.patchnote = """
**Gaming cog, first release!**

Main purpose of this cog is to help large gaming communities. There are two groups of commands at the moment `profiles` and `lfg`

`profiles` is used for managing gaming networks profiles, such as steam, psn, xbl, etx. I see it being used to get users profile, while he/she is away.
Use `[p]help profiles` for more info

`lfg` is a bit barebone at the moment. It can be used to set your status as "looking for group", so other users can see you on the list
Use `[p]help lfg` and `[p]help lfg looking` for more info

More to come!
"""

    # useful methids
    def savedb(self):
        """Save the db to file"""
        fileIO(self.dbpath, "save", self.db)

    # service stuff
    @commands.group(pass_context = True)
    async def gaming(self, ctx):
        """Returns info about the cog"""

        if ctx.invoked_subcommand is None:
            await self.bot.say("Type help gaming for info.")

    @gaming.command()
    async def info(self):
        """Returns the current version and patchnotes"""
        
        message = "Current cog version: **" + self.version + "**\n"
        message += "Patchnotes:"
        message += self.patchnote

        await self.bot.say(message)

    @gaming.command()
    async def ver(self):
        """Returns the current version"""

        message = "Current cog version: **" + self.version + "** (" + self.update_type + ")\n"
        message += "For patchnotes use `" + self.bot.command_prefix[0] + "gaming info`"
        await self.bot.say(message)

    @commands.group(pass_context = True)
    async def profiles(self, ctx):
        """Adds, edits and removes gaming network profile data"""

        if ctx.invoked_subcommand is None:
            await self.bot.say("Type help profile for info.")

    @profiles.command(pass_context = True)
    async def add(self, ctx, network, *, name):
        """Add a gaming network profile to DB. This is case-sensitive!
        Available networks:
            Steam,
            Battle.net,
            PSN,
            XBL,
            Origin,
            Uplay"""
        
        # perform settings check
        if ctx.message.server.id not in self.db.keys():
            self.db[ctx.message.server.id] = {}
        if "profiles" not in self.db[ctx.message.server.id].keys():
            self.db[ctx.message.server.id]["profiles"] = {}
        if ctx.message.author.id not in self.db[ctx.message.server.id]["profiles"].keys():
            self.db[ctx.message.server.id]["profiles"][ctx.message.author.id] = {}

        # clean the arg
        network = network.strip().lower()

        # check if network is correct
        if network in ["steam","battle.net","psn","xbl","origin","uplay"]:

            # check if already exists
            if network not in self.db[ctx.message.server.id]["profiles"][ctx.message.author.id]:

                # add and save
                self.db[ctx.message.server.id]["profiles"][ctx.message.author.id][network] = name.strip()
                fileIO("data/gaming/settings.json", "save", self.db)
                await self.bot.say("Profile saved\n"
                                   "Use `" + self.bot.command_prefix[0] + "profiles show` command "
                                   "to see all your profiles")

            else:
                await self.bot.say("Network already added\n"
                                   "Use `" + self.bot.command_prefix[0] + "profiles edit` command "
                                   "to edit existing profiles")
        else:
            await self.bot.say("Wrong network\n"
                               "Use `" + self.bot.command_prefix[0] + "help profiles add` command "
                               "to see the list of available networks")

    @profiles.command(pass_context = True)
    async def remove(self, ctx, network):
        """Removes a gaming network profile to DB. This is case-sensitive!
        Available networks:
            Steam,
            PSN,
            XBL,
            Origin,
            Uplay"""
        
        # perform settings check
        if ctx.message.server.id not in self.db.keys():
            self.db[ctx.message.server.id] = {}
        if "profiles" not in self.db[ctx.message.server.id].keys():
            self.db[ctx.message.server.id]["profiles"] = {}
        if ctx.message.author.id not in self.db[ctx.message.server.id]["profiles"].keys():
            self.db[ctx.message.server.id]["profiles"][ctx.message.author.id] = {}

        # clean the arg
        network = network.strip().lower()

        # check if network is correct
        if network in ["steam","psn","xbl","origin","uplay"]:

            # check if already exists
            if network in self.db[ctx.message.server.id]["profiles"][ctx.message.author.id]:

                # add and save
                self.db[ctx.message.server.id]["profiles"][ctx.message.author.id].pop(network, None)
                fileIO("data/gaming/settings.json", "save", self.db)
                await self.bot.say("Profile removed\n"
                                   "Use `" + self.bot.command_prefix[0] + "profiles show` command "
                                   "to see all your profiles")

            else:
                await self.bot.say("Profile not found\n"
                                   "Use `" + self.bot.command_prefix[0] + "profiles add` command "
                                   "to add new profile")
        else:
            await self.bot.say("Wrong network\n"
                               "Use `" + self.bot.command_prefix[0] + "help profiles remove` command "
                               "to see the list of available networks")

    @profiles.command(pass_context = True)
    async def show(self, ctx, user : discord.Member = None):
        """Shows all your gaming profiles, or those of a specified user"""
        
        # perform settings check
        if ctx.message.server.id not in self.db.keys():
            self.db[ctx.message.server.id] = {}
        if "profiles" not in self.db[ctx.message.server.id].keys():
            self.db[ctx.message.server.id]["profiles"] = {}

        # check if user was provided
        if user is None:
            user = ctx.message.author

        # check if already exists
        if user.id in self.db[ctx.message.server.id]["profiles"].keys():

            # show profiles
            message = "Showing gaming profiles for **" + user.name + "**\n```"
            for network in self.db[ctx.message.server.id]["profiles"][user.id].keys():
                message += network + " : " + self.db[ctx.message.server.id]["profiles"][user.id][network] + "\n"
            message += "```"

            await self.bot.say(message)

        else:
            # add empty profiles dict for future usage
            self.db[ctx.message.server.id]["profiles"][user.id] = {}
            fileIO("data/gaming/settings.json", "save", self.db)

            await self.bot.say("User not found\n"
                               "Use `" + self.bot.command_prefix[0] + "profiles add` command "
                               "to add the first profile")

    @profiles.command(pass_context = True)
    async def edit(self, ctx, network, *, name):
        """Edit a gaming network profile. This is case-sensitive!
        Available networks:
            Steam,
            Battle.net,
            PSN,
            XBL,
            Origin,
            Uplay"""
        
        # perform settings check
        if ctx.message.server.id not in self.db.keys():
            self.db[ctx.message.server.id] = {}
        if "profiles" not in self.db[ctx.message.server.id].keys():
            self.db[ctx.message.server.id]["profiles"] = {}



        if ctx.message.author.id in self.db[ctx.message.server.id]["profiles"].keys():

            # clean the arg
            network = network.strip().lower()

            # check if network is correct
            if network in ["steam","battle.net","psn","xbl","origin","uplay"]:

                # check if already exists
                if network in self.db[ctx.message.server.id]["profiles"][ctx.message.author.id]:

                    # edit and save
                    self.db[ctx.message.server.id]["profiles"][ctx.message.author.id][network] = name.strip()
                    fileIO("data/gaming/settings.json", "save", self.db)
                    await self.bot.say("Profile saved\n"
                                       "Use `" + self.bot.command_prefix[0] + "profiles show` command "
                                       "to see all your profiles")

                else:
                    await self.bot.say("Network is not added\n"
                                       "Use `" + self.bot.command_prefix[0] + "profiles add` command "
                                       "to add a new profile")
            else:
                await self.bot.say("Wrong network\n"
                                   "Use `" + self.bot.command_prefix[0] + "help profiles edit` command "
                                   "to see the list of available networks")

        else:
            # add empty profiles dict for future usage
            self.db[ctx.message.server.id]["profiles"][ctx.message.author.id] = {}
            fileIO("data/gaming/settings.json", "save", self.db)

            await self.bot.say("You haven't added any profiles yet\n"
                               "Use`" + self.bot.command_prefix[0] + "profiles add` command "
                               "to add the first profile")

    @commands.group(pass_context = True)
    async def lfg(self, ctx):
        """Manages LFG"""

        # perform settings check
        if ctx.message.server.id not in self.db.keys():
            self.db[ctx.message.server.id] = {}
        if "lfg" not in self.db[ctx.message.server.id].keys():
            self.db[ctx.message.server.id]["lfg"] = {
                "groups" : {},
                "looking" : {}
            }

        if ctx.invoked_subcommand is None:
            await self.bot.say("Type help lfg for info.")

    @lfg.command(pass_context = True)
    async def looking(self, ctx, action = None):
        """Sets looking for group status for you and shows people searching now
        Actions: start, stop, list
        Use without any options to see mount of people searching"""

        if action is not None:
            action = action.strip().lower()

        user = ctx.message.author
        
        # start search
        if action == "start":
            # check if already looking
            if ctx.message.author.id not in self.db[ctx.message.server.id]["lfg"]["looking"]:
                self.db[ctx.message.server.id]["lfg"]["looking"][ctx.message.author.id] = {
                    "name" : user.name,
                    "discriminator" : user.discriminator
                }
                self.savedb()
                await self.bot.say("You are now looking for group\n"
                                   "Use `" + self.bot.command_prefix[0] + "lfg looking list` command "
                                   "to see list of people searching")
            else:
                await self.bot.say("You are already looking for group\n"
                                   "Use `" + self.bot.command_prefix[0] + "lfg looking stop` command "
                                   "to stop looking for group now")

        # stop search
        elif action == "stop":
            # check if already looking
            if ctx.message.author.id in self.db[ctx.message.server.id]["lfg"]["looking"]:
                self.db[ctx.message.server.id]["lfg"]["looking"].pop(ctx.message.author.id, None)
                self.savedb()
                await self.bot.say("You are not looking for group anymore")
            else:
                await self.bot.say("You are not looking for group at the moment\n"
                                   "Use `" + self.bot.command_prefix[0] + "lfg looking start` command "
                                   "to start looking for group now")

        elif action == "list":
            # check if there are people looking
            if len(self.db[ctx.message.server.id]["lfg"]["looking"].keys()) > 0:
                #count people
                message = "There are **" + str(len(self.db[ctx.message.server.id]["lfg"]["looking"].keys())) + "** people "
                message += "looking for group at the moment\n"
                message += "```"
                # show the list
                for user in self.db[ctx.message.server.id]["lfg"]["looking"].keys():
                    user = self.db[ctx.message.server.id]["lfg"]["looking"][user]
                    message += user["name"] + " #" + user["discriminator"] + "\n"
                message += "```"
                await self.bot.say(message)
            else:
                await self.bot.say("There are no people looking for group at the moment\n"
                                   "Use `" + self.bot.command_prefix[0] + "lfg looking start` command "
                                   "to start looking for group now")
        else:
            # check if there are people looking
            if len(self.db[ctx.message.server.id]["lfg"]["looking"].keys()) > 0:
                #count people
                await self.bot.say("There are **" + str(len(self.db[ctx.message.server.id]["lfg"]["looking"].keys())) + "** people "
                                   "looking for group at the moment\n"
                                   "Use `" + self.bot.command_prefix[0] + "lfg looking list` command "
                                   "to show the full list")
            else:
                await self.bot.say("There are no people looking for group at the moment\n"
                                   "Use `" + self.bot.command_prefix[0] + "lfg looking start` command "
                                   "to start looking for group now")

    #TODO: add a twitch background generator
    #TODO: make per-server settings for userbars
    #TODO: refactor drawing functions, move similar code to shared functions
        
def check_folders():
    if not os.path.exists("data/gaming"):
        print("Creating data/gaming folder...")
        os.makedirs("data/gaming")

def check_files():
    f = "data/gaming/settings.json"
    if not fileIO(f, "check"):
        print("Creating settings.json...")
        fileIO(f, "save", {})

def setup(bot):
    check_folders()
    check_files()
    bot.add_cog(Gaming(bot))
