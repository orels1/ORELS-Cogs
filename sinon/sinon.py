import discord
from discord.ext import commands
from copy import copy
import asyncio
import os
from .utils.dataIO import fileIO
from aiohttp import web
from random import uniform
from random import randint
from tabulate import tabulate
try:
	from PIL import Image, ImageDraw, ImageFont
	pil_available = True
except:
	pil_available = False

class Sinon:
	"""Try \"s?\" if you're brave enough..."""

	def __init__(self, bot):
		self.bot = bot
		self.rpg = fileIO("data/sinon/rpg.json", "load")
		self.away = False

	# @commands.command(pass_context = True)
	# async def approach(self, ctx):
	# 	await self.bot.say("What?...")
	# 	await self.bot.send_file(ctx.message.channel, "data/sinon/myself.png")


	# @commands.command(pass_context = True)
	# async def say(self, ctx, *, message):
	# 	await self.bot.say("k...")
	# 	await self.bot.say(message)

	@commands.command()
	async def away(self):
		await self.bot.say("k... good luck out there...")
		self.bot.away = True

	# @commands.command()
	# async def back(self):
	# 	await self.bot.say("nice to see you again...")
	# 	self.bot.away = False

	# @commands.command(pass_context = True)
	# async def call(self, ctx, *, message):
	# 	await self.bot.say("s." + message)

	@commands.command(pass_context = True)
	async def shoot(self, ctx, user : discord.Member):
		await self.bot.say("confirmed...")
		await asyncio.sleep(1)
		await self.bot.say("target in sight...")
		await asyncio.sleep(1)
		await self.bot.say("kill confirmed...")
		await asyncio.sleep(1)
		await self.bot.say(user.mention + " was eliminated")
		await self.bot.send_file(ctx.message.channel, "data/sinon/shot.png")

	@commands.command(pass_context = True)
	async def says(self, ctx, *, message):
		print("dispatched!")
		print(message)

		await self.bot.say("k...")

		for c in self.bot.get_all_channels():
			if c.id == "133251234164375552":
				await self.bot.send_message(c, message)

	async def check_sinon(self, message):

		#orels1 = message.server.get_member("75887934410067968")

		async def bot_say(text):
			await self.bot.send_message(message.channel, text)

		async def s_talk(text, glitch = False, bold = False, extra = None, extra_bold = False):
			# check text length

				#get number of lines
				if text.count('\n') > 0:
					lines = text.count('\n')
				else:
					lines = 0

				if not glitch:
					cover = Image.open('data/sinon/sinon-eyes.png').convert('RGBA')
				else:
					cover = Image.open('data/sinon/sinon-glitch.png').convert('RGBA')

				if extra is None:
					extra_lines = 0
					result = Image.new('RGBA', (600, 172 + 32 * lines), (0,0,0))
					process = Image.new('RGBA', (600, 70 + 32 * lines), (0,0,0))
				else:
					extra_lines = extra.count('\n')
					result = Image.new('RGBA', (600, 242 + 32 * extra_lines), (0,0,0))
					process = Image.new('RGBA', (600, 140 + 30 * extra_lines), (0,0,0))

				# get a font
				if not bold:
					fnt = ImageFont.truetype('data/drawing/font.ttf', 37)
				else:
					fnt = ImageFont.truetype('data/drawing/font_bold.ttf', 37)

				if not extra_bold:
					fnt_extra = ImageFont.truetype('data/sinon/font_extra.ttf', 26)
				else:
					fnt_extra = ImageFont.truetype('data/sinon/font_extra_bold.ttf', 26)

				# get a drawing context
				d = ImageDraw.Draw(process)

				# draw text, half opacity
				d.rectangle([(0,0),(600,70 + 32 * (lines + extra_lines))], fill=(0,0,0,160))
				d.text((25,20), text, font=fnt, fill=(255,255,255,255))
				d.rectangle([(10,10),(590, 70 + 32 * lines - 10)], fill=None, outline=(200,200,200,128))

				if extra:
					d.rectangle([(10, 70 + 32 * lines - 10), (590, 70 + 30 * (lines + extra_lines) - 10)], fill=None, outline=(200,200,200,128))
					d.text((20,70 + 35 * lines - 10), extra, font=fnt_extra, fill=(255,255,255,255))

				result.paste(cover, (0,0))
				result.paste(process, (0,102))

				result.save('temp.jpg','JPEG', quality=100)

				await self.bot.send_file(message.channel, 'temp.jpg')

				os.remove('temp.jpg')

		if "sinon" in message.content.split() and "s.reload" not in message.content.split():
			imgurclient = ImgurClient("1fd3ef04daf8cab", "f963e574e8e3c17993c933af4f0522e1dc01e230")
			items = imgurclient.gallery_search("sinon", advanced=None, sort='time', window='all', page=0)
			if len(items) < 1:
				await self.bot.send_message(message.channel, "Your search terms gave no results.")
			else:
				rand = randint(0, len(items) -1)
				async def check_nsfw(items, num):
					if items[num].nsfw or items[num].is_album or items[num].ups < 10:
						num = randint(0, len(items) -1)
						await check_nsfw(items, num)
					else:
						await self.bot.send_message(message.channel,items[num].link)

				await check_nsfw(items, rand)

		#the magic starts here, wanna join?
		if "s?" in message.content.split()[:1]:
			#await self.bot.send_message(message.channel, "What?...")
			await s_talk("what?...")

			def show_shop():
				table = []
				for item in enumerate(self.rpg["shop"]["items"]):
					table.append([
							item[0],
							item[1]["name"],
							"+" + str(item[1]["atk"]),
							str(item[1]["price"]) + " COL.",
							item[1]["stock"]
						])
				resp = "```"
				resp += tabulate(table, headers = ["#","Item","Attack","Price","In stock"], tablefmt="fancy_grid")
				resp += "```"
				return resp

			#TODO: Combine with show_shop
			def get_items(char):
				table = []
				for item in enumerate(char["items"]):
					table.append([
							item[0],
							item[1]["name"],
							item[1]["atk"],
							item[1]["stock"]
						])
				return table

			def get_chars(user):
				table = []
				print("Getting chars for user "+ str(user))
				print(self.rpg["players"][str(user)])
				for char in enumerate(self.rpg["players"][str(user)]):
					print(char)
					table.append([
							char[0],
							char[1]["name"],
							char[1]["lvl"],
							char[1]["stats"]["hp"],
							char[1]["stats"]["atk"],
							char[1]["stats"]["def"],
							str(char[1]["bank"]) + " COL."
						])
					if char[1]["active"]:
						table[char[0]][1] = "-> " + table[char[0]][1]

				return table

			def create_char(charname):
				#form char dict
				char = {
					"name" : charname,
					"lvl" : 1,
					"stats" : {
						"atk" : 1,
						"def" : 1,
						"hp" : 100
					},
					"active" : False,
					"bank" :  1000
				}

				#if no chars
				if str(message.author.id) not in self.rpg["players"].keys():
					char["id"] = 0
					self.rpg["players"][str(message.author.id)] = [char]

				#if second+ char
				else:
					char["id"] = len(self.rpg["players"][str(message.author.id)])
					self.rpg["players"][str(message.author.id)].append(char)

			async def buy_item(item, char):
				#copy for local changes
				player_item = copy(item)

				#check balance
				if char["bank"] >= item["price"]:
					self.rpg["players"][str(message.author.id)][char["id"]]["bank"] -= item["price"]

					#change shop's stock
					item["stock"] -= 1

					#if no items
					if "items" not in char.keys():
						#modify stock
						player_item["stock"] = 1
						self.rpg["players"][str(message.author.id)][char["id"]]["items"] = [player_item]

					#if has items
					else:
						bought = False
						#check if duplicate
						for it in enumerate(char["items"]):
							if item["name"] == it[1]["name"]:
								#add one more
								print("duplicate!")
								self.rpg["players"][str(message.author.id)][char["id"]]["items"][it[0]]["stock"] += 1
								bought = True

						#if there were np duplicates
						if not bought:
							#add just one
							player_item["stock"] = 1
							print(player_item)
							self.rpg["players"][str(message.author.id)][char["id"]]["items"].append(player_item)

					await bot_say("everything is fine... " + item["name"] + " is yours now")

					#save here
					save(self.rpg)
				else:
					await bot_say("you don't have the funds... don't mess around...")

			def check_login(user):
				#find logged in char
				for char in enumerate(self.rpg["players"][user]):
					if char[1]["active"]:
						return {"logged_in": True, "char": char[1]}
				#if not logged in
				return {"logged_in": False, "char": {}}	

			def upd_stats(char):
				#safe-check if there are items
				if "items" in char.keys():
					if len(char["items"]) > 0:
						
						#calculate total ATK value
						total_atk = 1
						for item in char["items"]:
							total_atk += item["atk"]
						
						#check if is different
						if not total_atk == char["stats"]["atk"]:
							char["stats"]["atk"] = total_atk

						#save here
						save(self.rpg)

			async def perform_fight(attacker, victim):
				table = [
					[
						attacker["name"],
						" VS ",
						victim["name"]
					],
					[
						"ATK " + str(attacker["stats"]["atk"]),
						"",
						"ATK " + str(victim["stats"]["atk"])
					]
				]

				resp = "seems like we finally have a fight...\n\n"
				resp += "```"
				resp += tabulate(table, headers=["NEW","--","FIGHT"], tablefmt="fancy_grid")
				resp += "```"

				await bot_say(resp)

				#calculate luck
				attack_luck = uniform(0.92,1)
				victim_luck = uniform(0.92,1)

				attack_atk = attacker["stats"]["atk"] * attack_luck
				victim_atk = victim["stats"]["atk"] * victim_luck

				#show attacks
				resp = "\n" + attacker["name"] + " hits for " + "%.4f" % round(attack_atk, 4)
				if (attack_luck >= 0.98): resp += " **CRIT!**"
				resp += "\n" + victim["name"] + " hits for " + "%.4f" % round(victim_atk, 4)
				if (victim_luck >= 0.98): resp += " **CRIT!**"
				resp += "\n\n"
				
				#determine winner
				if attack_atk > victim_atk:
					resp += "**" + attacker["name"] + " WINS!**"
				elif attack_atk < victim_atk:
					resp += "**" + victim["name"] + " WINS!**"
				else:
					resp += "**DRAW!**"

				await bot_say(resp)

				#save here
				save(self.rpg)
						

			def is_number(s):
						try:
							int(s)
							return True
						except ValueError:
							return False

			def save(state):
				fileIO("data/sinon/rpg.json", "save", state)

			answer = await self.bot.wait_for_message(timeout=15, author=message.author)
			#put it in variable for ease of use
			a_list = answer.content.lower().split()

			if "who" in a_list:
				#get proper name
				if a_list[-1:][0][-1:] == "?":
					name = a_list[-1:][0][:-1]
				else:
					name = a_list[-1:][0]

				#check if answer is defined
				if name in self.rpg["people"].keys():
					if name in ["26", "twentysix", "twentysix26"]:
						await s_talk(self.rpg["people"][name], glitch = True)
					else:
						await bot_say(self.rpg["people"][name])
				else:
					await bot_say("i have no interest in that one...")

			elif "login" in a_list:

				#check if user have any chars
				if message.author.id in self.rpg["players"].keys():
					
					#upd stats just in case
					for char in self.rpg["players"][str(message.author.id)]:
						upd_stats(char)

					await s_talk("k... here are your options...")

					#form chars array
					chars_list = get_chars(message.author.id)

					resp = "```"
					resp += tabulate(chars_list, headers = ["#","Name","LvL","HP","ATK","DEF","Bank"], tablefmt="fancy_grid")
					resp += "```"

					await bot_say(resp + "\nwhich one?...")

					answer = await self.bot.wait_for_message(timeout=15, author=message.author)

					#check if user entered proper number
					if is_number(answer.content.lower().split()[0]):
						char_num = int(answer.content.lower().split()[0])

						#check if proper char
						if char_num <= (len(chars_list) - 1):

							#check if not already logged in
							if not self.rpg["players"][str(message.author.id)][char_num]["active"]:

								await s_talk("logging in with " + chars_list[char_num][1] + "\nhave fun...")

								#logout of other chars
								for char in self.rpg["players"][str(message.author.id)]:
									if char["active"]:
										char["active"] = False

								#login into char		
								self.rpg["players"][str(message.author.id)][char_num]["active"] = True

								#don't forget to save
								save(self.rpg)
							else:
								await s_talk("you are already playing this one...")
						else:
							await s_talk("stop fooling around... there is no such char...")
					else:
						await s_talk("stop fooling around... there is no such char...")
					

				else:
					await s_talk("no characters... wanna come with me?... yes or no...")

					answer = await self.bot.wait_for_message(timeout=15, author=message.author)

					#create new char
					if "yes" in answer.content.lower():
						await s_talk("I will need your name... just one word...")

						answer = await self.bot.wait_for_message(timeout=15, author=message.author)						

						#add to current dicr
						create_char(answer.content.split()[0])

						#save here
						save(self.rpg)

						#all good
						await s_talk("good... don't forget to login... and good luck...")

					else:
						await s_talk("just like I thought...")

			elif "create" in a_list:
				await s_talk("wanna come with me?...\nI will need your name... just one word...")

				answer = await self.bot.wait_for_message(timeout=15, author=message.author)						

				#add to current dict
				create_char(answer.content.split()[0])

				#save here
				save(self.rpg)

				#all good
				await s_talk("good... don't forget to login... and good luck...")


			elif "shop" in a_list:
				#get logged in char
				login = check_login(str(message.author.id))

				if self.rpg["shop"]["opened"]:
					if login["logged_in"]:
						await bot_say("ok... but be quick...")
						await asyncio.sleep(1)
						await bot_say("this is what i have...\n" + show_shop() + "\n interested?...")

						answer = await self.bot.wait_for_message(timeout=15, author=message.author)

						#check if user entered proper number
						if is_number(answer.content.lower().split()[0]):
							item_num = int(answer.content.lower().split()[0])

							#check if proper item
							if item_num <= (len(self.rpg["shop"]["items"]) - 1):
								#buy item for char
								await buy_item(self.rpg["shop"]["items"][item_num], login["char"])
							else:
								await bot_say("stop fooling around... there is no such item...")

						else:
							await bot_say("stop fooling around... there is no such item...")
					else:
						await bot_say("stop fooling around... login first...")

				else:
					await bot_say("my shop is closed for now...")

			elif "reload" in a_list:
				self.rpg = fileIO("data/sinon/rpg.json", "load")			
				await s_talk("db reloaded", glitch = True, bold = True)

			elif "inventory" in a_list:
				login = check_login(str(message.author.id))
				if login["logged_in"]:

					#upd stats just in case
					upd_stats(login["char"])

					if "items" in login["char"]:
						resp = "```"
						resp += tabulate(get_items(login["char"]), headers=["Name","ATK","Stock"], tablefmt="fancy_grid")
						resp += "```"
						await bot_say("this is what you got...\n\n" + resp)
					else:
						await bot_say("you dont have any items... buy some first...")

				else:
					await bot_say("stop fooling around... login first...")

			elif "char" in a_list:
				login = check_login(str(message.author.id))
				if login["logged_in"]:

					#upd stats just in case
					upd_stats(login["char"])

					table = [
						[str(login["char"]["stats"]["hp"]) + " HP"],
						[str(login["char"]["stats"]["atk"]) + " ATK"],
						[str(login["char"]["stats"]["def"]) + " DEF"],
						[str(login["char"]["bank"]) + " COL."],
					]

					resp = "```"
					resp += tabulate(table, headers=[login["char"]["name"] + " [LvL. " + str(login["char"]["lvl"]) + "]"], tablefmt="fancy_grid")
					resp += "```"

					await bot_say("really?... k... go ahead... admire yourself...\n\n" +  resp)

				else:
					await bot_say("stop fooling around... login first...")


			elif "fight" in a_list:
				login = check_login(str(message.author.id))

				if login["logged_in"]:

					#upd stats just in case
					upd_stats(login["char"])

					#check if in public channel
					if not message.channel.is_private:

						#check if has a mention
						if a_list[-1:][0][:2] == "<@":

							#check if oppenent is playing
							if a_list[-1:][0][2:-1] in self.rpg["players"].keys():
								attacker = login["char"]
								victim = check_login(a_list[-1:][0][2:-1])["char"]
								#upd stats just in case
								upd_stats(victim)

								#hand it off to fighting function
								await perform_fight(attacker, victim)

							else:
								await bot_say("that one is too afraid to play with me...")
						else:
							await bot_say("choose an opponent...")
					else:
						await bot_say("find a public place to fight...")

				else:
					await bot_say("stop fooling around... login first...")

			elif "help" in a_list:
				login = check_login(str(message.author.id))

				#parse commands
				table = []
				for command in self.rpg["commands"]:
					table.append([command["name"], command["help"]])

				#from menu table
				resp = "SINON RPG-MODE v.0.0.1\n"
				if login["logged_in"]:
					resp += "You are logged in as " + login["char"]["name"]
				else:
					resp += "You are not logged in atm"

				await s_talk(resp, glitch=True, bold=True, extra=tabulate(table, tablefmt="grid"))

			else:
				await s_talk("whatever...")

def check_folders():
	if not os.path.exists("data/sinon"):
		print("Creating data/sinon folder...")
		os.makedirs("data/sinon")

def check_files():
	f = "data/issues/rpg.json"
	if not fileIO(f, "check"):
		print("Creating empty rpg.json...")
		fileIO(f, "save", [])

def setup(bot):
	check_files()
	check_folders()
	global ImgurClient
	try:
		from imgurpython import ImgurClient
	except:
		raise ModuleNotFound("imgurpython is not installed. Do 'pip3 install imgurpython' to use this cog.")
	if pil_available is False:
		raise RuntimeError("You don't have Pillow installed, run\n```pip3 install pillow```And try again")
		return
	n = Sinon(bot)
	bot.add_listener(n.check_sinon, "on_message")
	bot.add_cog(n)
