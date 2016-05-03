import discord
from discord.ext import commands
import asyncio
import os
import math
import aiohttp
try:
    from PIL import Image, ImageDraw, ImageFont
    pil_available = True
except:
    pil_available = False


class Drawing:
    """Draw images and text"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context = True)
    async def text(self, ctx, *, text, bg="black"):
        """Draws text on a background. Black by default"""

        # check text length

        if len(text) > 24:
            await self.bot.say("Too big for me")
        else:

            result = Image.open('data/drawing/bg.png').convert('RGBA')

            process = Image.new('RGBA', (400,100), (0,0,0))

            # get a font
            fnt = ImageFont.truetype('data/drawing/font.ttf', 37)
            fnt_sm = ImageFont.truetype('data/drawing/font.ttf', 20)
            # get a drawing context
            d = ImageDraw.Draw(process)

            # draw text, half opacity
            d.rectangle([(0,0),(400,100)], fill=(0,0,0,160))
            d.text((25,25), "«" + text + "»", font=fnt, fill=(255,255,255,255))
            d.text((320, 65), "— Sinon", font=fnt_sm, fill=(255,255,255,128))
            d.rectangle([(10,10),(390,90)], fill=None, outline=(200,200,200,128))

            result = Image.alpha_composite(result, process)

            result.save('temp.jpg','JPEG', quality=100)

            await self.bot.send_file(ctx.message.channel, 'temp.jpg')

            os.remove('temp.jpg')

    @commands.command(pass_context = True)
    async def build(self, ctx, additional = None):
        """Image builder. Add \"meme\" for meme creation"""

        await self.bot.say("Please send the bg image")
        answer = await self.bot.wait_for_message(timeout=30, author=ctx.message.author)        
        bg_url = answer.attachments[0]["url"]
        bg_image = Image

        success = False
        try:
            async with aiohttp.get(bg_url) as r:
                image = await r.content.read()
            with open('data/drawing/temp_bg','wb') as f:
                f.write(image)
                bg_image = Image.open('data/drawing/temp_bg').convert('RGBA')
                success = True

        except Exception as e:
            success = False
            print(e)
            

        if success:
            # define vars
            title = ""
            subtitle = ""

            # get vars
            await self.bot.say("Please type title")
            answer = await self.bot.wait_for_message(timeout=30, author=ctx.message.author)
            title = answer.content.lower().strip()

            await self.bot.say("Please type subtitle")
            answer = await self.bot.wait_for_message(timeout=30, author=ctx.message.author)
            subtitle = answer.content.lower().strip()

            # check text length
            if len(title) < 30 and len(subtitle) < 40:
                    
                result = bg_image

                new_width = 650
                new_height = int(math.floor((result.size[1] / result.size[0]) * new_width))


                if new_height < 366:
                    new_height = 366
                    new_width = int(math.floor((result.size[0] / result.size[1]) * new_height))

                half_width = int(math.floor(new_width / 2))
                half_height = int(math.floor(new_height /2))

                result = result.resize(size=(new_width, new_height))
                print("Feature dimensions", new_width, "by", new_height)

                process = Image.new('RGBA', (new_width,new_height), (0,0,0))
                print("Overlay dimensions", process.size)
                print("Modes are", result.mode, "and", process.mode)

                # get a font
                fnt = ImageFont.truetype('data/drawing/font.ttf', 70)
                fnt_sm = ImageFont.truetype('data/drawing/font.ttf', 40)
                fnt_b = ImageFont.truetype('data/drawing/font_bold.ttf', 70)
                fnt_meme = ImageFont.truetype('data/drawing/font_bold.ttf', 55)
                # get a drawing context
                d = ImageDraw.Draw(process)

                # calculate text sizes and positions
                author_pos = int(math.floor(fnt_sm.getsize(ctx.message.author.name)[0] / 2))
                title_pos = int(math.floor(fnt_b.getsize(title)[0] / 2))
                subtitle_pos = int(math.floor(fnt_sm.getsize(subtitle)[0] / 2))

                if additional is not None and additional.lower().strip() == "meme":

                    # haax
                    d.rectangle([(0,0),(new_width,new_height)], fill=(0,0,0,0))

                    # overwrite needed titles
                    title_pos = int(math.floor(fnt_meme.getsize(title)[0] / 2))
                    subtitle_pos = int(math.floor(fnt_meme.getsize(subtitle)[0] / 2))

                    # dark bgs
                    d.rectangle([(10,10),(new_width - 10,80)], fill=(0,0,0,160))
                    d.rectangle([(10, new_height - 80),(new_width - 10, new_height - 10)], fill=(0,0,0,160))
                    
                    # text
                    d.text((half_width - title_pos, 25), title, font=fnt_meme, fill=(255,255,255,255))
                    d.text((half_width - subtitle_pos, new_height - 65), subtitle, font=fnt_meme, fill=(255,255,255,255))

                else:

                    # dark filter
                    d.rectangle([(0,0),(new_width,new_height)], fill=(0,0,0,140))

                    # darker inner
                    d.rectangle([(20,20),(new_width - 20, new_height - 20)], fill=(0,0,0,180), outline=(200,200,200,128))

                    # text
                    d.text((half_width - author_pos, half_height - 60), ctx.message.author.name, font=fnt_sm, fill=(255,255,255,255))
                    d.text((half_width - title_pos, half_height - 20), title, font=fnt_b, fill=(255,255,255,255))
                    d.text((half_width - subtitle_pos, half_height + 40), subtitle, font=fnt_sm, fill=(255,255,255,255))

                print("Final overlay mode", process.mode)
                print("Final overlay size", process.size)

                result = Image.alpha_composite(result, process)

                result.save('temp.jpg','JPEG', quality=100)

                await self.bot.send_file(ctx.message.channel, 'temp.jpg')

                os.remove('temp.jpg')
                os.remove('temp_bg.jpg')

            else:
                await self.bot.say("Too big for me")

        else:
            await self.bot.say("Error getting image")

    @commands.command(pass_context=True)
    async def userbar(self, ctx, alt = None):
        """Generates a server-based userbar"""

        # get an avatar
        avatar_url = ctx.message.author.avatar_url
        avatar_image = Image

        #get server icon
        server_url = ctx.message.server.icon_url
        server_image = Image

        # get images
        try:
            async with aiohttp.get(avatar_url) as r:
                image = await r.content.read()
            with open('data/drawing/temp_avatar','wb') as f:
                f.write(image)
                success = True
        except Exception as e:
            success = False
            print(e)

        try:
            async with aiohttp.get(server_url) as r:
                image = await r.content.read()
            with open('data/drawing/temp_server','wb') as f:
                f.write(image)
                success = True
        except Exception as e:
            success = False
            print(e)

        if success:

            # load images
            avatar_image = Image.open('data/drawing/temp_avatar').convert('RGBA')
            server_image = Image.open('data/drawing/temp_server').convert('RGBA')

            # get a font
            fnt = ImageFont.truetype('data/drawing/font.ttf', 25)
            fnt_sm = ImageFont.truetype('data/drawing/font.ttf', 18)
            fnt_b = ImageFont.truetype('data/drawing/font_bold.ttf', 25)

            if alt is None:
                # prepare canvas to work with
                result = Image.new('RGBA', (400, 100), (0,0,0,255))
                process = Image.new('RGBA', (400, 100), (0,0,0,255))

                # get a drawing context
                d = ImageDraw.Draw(process)

                # haax
                d.rectangle([(0,0), (400,100)])

                # paste background (server icon) to final image 
                server_image = server_image.resize(size=(100,100))               
                result.paste(server_image, (0,0))

                # draw filter
                d.rectangle([(0,0),(400,100)], fill=(0,0,0,160))

                # draw overlay
                d.rectangle([(10,10),(390,90)], fill=(0,0,0,190), outline=(200,200,200,128))

                 # paste avatar
                avatar_image = avatar_image.resize(size=(60,60))
                process.paste(avatar_image, (20,20))

                # get role
                roles = ctx.message.author.roles
                if len(roles) == 1:
                    role = "member"
                else:
                    max_role = max([r.position for r in roles])
                    index = [r.position for r in roles].index(max_role)
                    role = roles[index].name

                # draw text
                name_size = fnt_b.getsize(ctx.message.author.name)[0]
                d.text((110, 30), ctx.message.author.name, font=fnt_b, fill=(255,255,255,255))
                d.text((110 + name_size + 10, 33), "#" + ctx.message.author.discriminator, font=fnt_sm, fill=(255,255,255,128))
                d.text((110, 60), "A proud " + role + " of " + ctx.message.server.name, font=fnt_sm, fill=(255,255,255,180))

            else:
                # prepare canvas to work with
                result = Image.new('RGBA', (200,200), (0,0,0))
                process = Image.new('RGBA', (200,200), (0,0,0))

                # get a drawing context
                d = ImageDraw.Draw(process)

                # haax
                d.rectangle([(0,0), (200,200)])

                # paste background (server icon) to final image
                server_image = server_image.resize(size=(200,200))
                result.paste(server_image, (0,0))

                # draw filter
                d.rectangle([(0,0),(200,200)], fill=(0,0,0,160))

                #draw overlay
                d.rectangle([(10,10),(190,190)], fill=(0,0,0,190), outline=(200,200,200,128))

                # paste avatar
                avatar_image = avatar_image.resize(size=(100,100))
                process.paste(avatar_image, (50,25))

                # draw text
                name_pos = int(math.floor(fnt_b.getsize(ctx.message.author.name)[0] / 2))
                discr_pos = int(math.floor(fnt_sm.getsize("#"+ctx.message.author.discriminator)[0] / 2))
                d.text((100 - name_pos, 140), ctx.message.author.name, font=fnt_b, fill=(255,255,255,255))
                d.text((100 - discr_pos, 162), "#" + ctx.message.author.discriminator, font=fnt_sm, fill=(255,255,255,128))

            result = Image.alpha_composite(result, process)

            result.save('data/drawing/temp.jpg','JPEG', quality=100)

            await self.bot.send_file(ctx.message.channel, 'data/drawing/temp.jpg')

            os.remove('data/drawing/temp.jpg')
            os.remove('data/drawing/temp_avatar')
            os.remove('data/drawing/temp_server')

        else:
            await self.bot.say("Couldn't get images")

def setup(bot):
    if pil_available is False:
        raise RuntimeError("You don't have Pillow installed, run\n```pip3 install pillow```And try again")
        return
    bot.add_cog(Drawing(bot))
