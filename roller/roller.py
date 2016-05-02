import discord
from discord.ext import commands
import random

class Roller:
	"""Rolling dices, the right way"""

	def __init__(self, bot):
		self.bot = bot
		self.roll_arr = []

	# Dice rolling function
	def roll_dice(self, count, dice, mod, result):
		# extra rolls check
		extra_rolls = 0

		# perform rolls
		for i in range(0, count):
			roll = random.randint(1, dice)

			# check if hit max for extra roll
			if roll == dice:
				extra_rolls += 1

			# add roll modifier
			roll += mod
			
			result.append(roll)

		# roll extra
		if extra_rolls > 0:
			self.roll_dice(extra_rolls, dice, mod, result)
		else:
			self.roll_arr = result

	@commands.command(pass_context = True)
	async def rd(self, ctx, count=4, dice=20, mod=0):
		"""
			Rolls dices in the XdY+MOD style
			By default rolls 4d20 with MOD=0
		"""

		def is_number(s):
			try:
				int(s)
				return True
			except ValueError:
				return False
		
		# Check if provided with numbers
		if is_number(count) and is_number(dice) and is_number(mod):
			
			# check if numbers are correct
			if int(count) > 0 and int(count) <= 50 and int(dice) > 0 and int(dice) <= 50 and int(mod) >= 0:
				# Delete old roll
				self.roll_arr = []

				# Roll the dice
				self.roll_dice(int(count), int(dice), int(mod), [])

				message = "**[" + "]** **[".join(str(roll) for roll in self.roll_arr) + "]**"

				await self.bot.say("You rolled: \n" + message)
			else:
				await self.bot.say("Dice and side amount should be in range from 0 to 50. Mod should be > 0")

		else:
			await self.bot.say("Please provide numbers in format <amount of dices> <number of sides> <modifier>\nMax value is 50")

	@commands.command(pass_context = True)
	async def rds(self, ctx, count=4, dice=20, mod=0, success=10):
		"""
			Check if was successfull based on a success rate
			By default rolls 4d20 with MOD=0 and checks for 10 as a success value
		"""

		def is_number(s):
			try:
				int(s)
				return True
			except ValueError:
				return False
		
		# Check if provided with numbers
		if is_number(count) and is_number(dice) and is_number(mod) and is_number(success):

			# check if numbers are correct
			if int(count) > 0 and int(count) <= 50 and int(dice) > 0 and int(dice) <= 50 and int(mod) >= 0 and int(success) > 0:

				# Delete old roll
				self.roll_arr = []

				# Roll the dice
				self.roll_dice(int(count), int(dice), int(mod), [])

				# check for values that passed
				passed = 0
				for roll in self.roll_arr:
					if roll >= int(success):
						passed += 1
					else:
						continue

				if passed >= int(len(self.roll_arr) / 2):
					await self.bot.say("Success! (" + " ".join(str(roll) for roll in self.roll_arr) + ")")
				else:
					await self.bot.say("Fail! (" + " ".join(str(roll) for roll in self.roll_arr) + ")")

			else:
				await self.bot.say("Dice and side amount should be in range from 0 to 50. Mod and success should be > 0")


		else:
			await self.bot.say("Please provide numbers in format <amount of dices> <number of sides> <modifier> <success threshold>\nMax value is 50")

	@commands.command(pass_context = True)
	async def last(self, ctx):
		"""Shows last roll"""
		await self.bot.say("Last roll:\n**[" + "]** **[".join(str(roll) for roll in self.roll_arr) + "]**")


def setup(bot):
	bot.add_cog(Roller(bot))
