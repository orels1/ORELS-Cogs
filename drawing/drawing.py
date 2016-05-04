import discord
from discord.ext import commands
import asyncio
import os
import math
import aiohttp
from copy import copy
try:
    from PIL import Image, ImageDraw, ImageFont, ImageColor
    pil_available = True
except:
    pil_available = False


class Drawing:
    """Draw images and text"""

    def __init__(self, bot):
        self.bot = bot
        self.version = "1.1.0"
        self.patchnote = """
            **A lot of imporvements**
            Added new build command `screen`, which overlays your name on a screenshot
            Can also add gamename if provided as an argument and crop window frames if you happen to screenshot a window
            Example usage (with game and crop):
            ```
            [p]screen overwatch crop```

            Added a rickroll command, just for pure dankness

            Userbar now supports custom backgrounds. You can create it with a speciefic color like this:
            ```
            [p]userbar #2980b9```
            Or you can change the image like that:
            ```
            [p]userbar custom```
            Only 400x100 images will be accepted

            Hope you'll like it! More to come!
        """

    @commands.group(pass_context = True)
    async def drawing(self, ctx):
        """Returns info about the cog"""

        if ctx.invoked_subcommand is None:
            await self.bot.say("Type help drawing for info.")

    @drawing.command(name = 'info')
    async def info(self):
        """Returns the current version and patchnotes"""

        message = "Current cog version: **" + self.version + "**\n"
        message += "Patchones:"
        message += self.patchnote

        await self.bot.say(message)


    @commands.command(pass_context = True)
    async def text(self, ctx, *, text):
        """Draws text on a background"""

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

            result.save('data/drawing/temp.jpg','JPEG', quality=100)

            await self.bot.send_file(ctx.message.channel, 'temp.jpg')

            os.remove('data/drawing/temp.jpg')

    @commands.group(pass_context = True)
    async def build(self, ctx):
        """Generates fancy images"""

        if ctx.invoked_subcommand is None:
            await self.bot.say("Type help build for info.")

    @build.command(name = 'meme', pass_context = True)
    async def meme(self, ctx):
        """Meme builder."""

        await self.bot.say("Please send the background")
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
            await self.bot.say("Please type firs line of txt")
            answer = await self.bot.wait_for_message(timeout=30, author=ctx.message.author)
            title = answer.content.lower().strip()

            await self.bot.say("Please type second line of texe")
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
                fnt_meme = ImageFont.truetype('data/drawing/font_bold.ttf', 55)
                # get a drawing context
                d = ImageDraw.Draw(process)

                # haax
                d.rectangle([(0,0),(new_width,new_height)], fill=(0,0,0,0))

                # calculate text positions
                title_pos = int(math.floor(fnt_meme.getsize(title)[0] / 2))
                subtitle_pos = int(math.floor(fnt_meme.getsize(subtitle)[0] / 2))

                # dark bgs
                d.rectangle([(10,10),(new_width - 10,80)], fill=(0,0,0,160))
                d.rectangle([(10, new_height - 80),(new_width - 10, new_height - 10)], fill=(0,0,0,160))
                
                # text
                d.text((half_width - title_pos, 25), title, font=fnt_meme, fill=(255,255,255,255))
                d.text((half_width - subtitle_pos, new_height - 65), subtitle, font=fnt_meme, fill=(255,255,255,255))

                # blend bg and text
                result = Image.alpha_composite(result, process)

                # save and send
                result.save('temp.jpg','JPEG', quality=100)
                await self.bot.send_file(ctx.message.channel, 'temp.jpg')

                # cleanup
                os.remove('temp.jpg')
                os.remove('temp_bg.jpg')

            else:
                # pun intended
                await self.bot.say("Too big for me")

        else:
            await self.bot.say("Error getting image")

    @build.command(name = 'feature', pass_context = True)
    async def feature(self, ctx):
        """Fancy features builder"""

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

                # dark filter
                d.rectangle([(0,0),(new_width,new_height)], fill=(0,0,0,140))

                # darker inner
                d.rectangle([(20,20),(new_width - 20, new_height - 20)], fill=(0,0,0,180), outline=(200,200,200,128))

                # text
                d.text((half_width - author_pos, half_height - 60), ctx.message.author.name, font=fnt_sm, fill=(255,255,255,255))
                d.text((half_width - title_pos, half_height - 20), title, font=fnt_b, fill=(255,255,255,255))
                d.text((half_width - subtitle_pos, half_height + 40), subtitle, font=fnt_sm, fill=(255,255,255,255))

                result = Image.alpha_composite(result, process)

                # save and send
                result.save('temp.jpg','JPEG', quality=100)
                await self.bot.send_file(ctx.message.channel, 'temp.jpg')

                # cleanup
                os.remove('temp.jpg')
                os.remove('temp_bg.jpg')

            else:
                # pun intended
                await self.bot.say("Too big for me")

        else:
            await self.bot.say("Error getting image")

    @build.command(name = 'screen', pass_context = True)
    async def screen(self, ctx, game = None, cut_window = None):
        """Personalized image branding with widow borders as an option"""

        await self.bot.say("Please send the screnshot")
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
                    
            # will draw on source
            result = bg_image

            half_width = int(math.floor(result.size[0] / 2))
            half_height = int(math.floor(result.size[1] /2))

            # if need to cut window borders - do so
            if cut_window is not None:
                result = result.crop((1,31,result.size[0] - 1, result.size[1] - 1))

            width = result.size[0]
            height = result.size[1]

            # create a new canvas
            process = Image.new('RGBA', (width, height), (0,0,0))

            # get fonts
            fnt = ImageFont.truetype('data/drawing/font.ttf', 30)
            fnt_b = ImageFont.truetype('data/drawing/font_bold.ttf', 40)

            # get a drawing context
            d = ImageDraw.Draw(process)

            #haax
            d.rectangle([(0,0),(width, height)], fill=(0,0,0,0))

            # calculate text sizes and positions
            author_width = fnt_b.getsize(ctx.message.author.name)[0]

            # dark overlay
            d.rectangle([(0,height - 70),(width,height)], fill=(0,0,0,140))

            # text
            d.text((20, height - 50), ctx.message.author.name, font=fnt_b, fill=(255,255,255,255))
            d.text((20 + author_width + 20, height - 47), "#" + ctx.message.author.discriminator, font=fnt, fill=(255,255,255,200))

            # if provided a game name - draw it
            if game is not None:
                game_width = fnt_b.getsize(game.strip())[0]
                d.text((width - game_width - 20, height - 50), game.strip(), font=fnt_b, fill=(255,255,255,255))

            result = Image.alpha_composite(result, process)

            # save and send
            result.save('data/drawing/temp.jpg','JPEG', quality=100)
            await self.bot.send_file(ctx.message.channel, 'data/drawing/temp.jpg')

            # cleanup
            os.remove('data/drawing/temp.jpg')
            os.remove('data/drawing/temp_bg.jpg')

        else:
            await self.bot.say("Error getting image")

    @commands.command(pass_context=True)
    async def userbar(self, ctx, background = None):
        """Generates a server-based userbar, you can provide a backround color as rgba (0-255,0-255,0-255,0-255)"""

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

            # set background
            bg_color = (0,0,0,255)
            if background is not None:
                
                if background  != "custom":
                    print(background)
                    c = ImageColor.getrgb(background.strip())
                    bg_color = (c[0],c[1],c[2],255)

            # prepare canvas to work with
            result = Image.new('RGBA', (400, 100), bg_color)
            process = Image.new('RGBA', (400, 100), bg_color)

            # get a drawing context
            d = ImageDraw.Draw(process)

            # haax
            d.rectangle([(0,0), (400,100)])

            # paste background (server icon) to final image if background is not provided
            if background is None:
                server_image = server_image.resize(size=(100,100))               
                result.paste(server_image, (0,0))
            
            # if background should be provided by user
            elif background == "custom":
                await self.bot.say("Please send the background. It should be 400x100")
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

                    #check image dimensions
                    if bg_image.size == (400,100):

                        result.paste(bg_image, (0,0))

                    else:
                        result.paste(server_image, (0,0))
                        await self.bot.say("Image dimensions incorrect, using defaults. Image has to be 400x100")

                else:
                    result.paste(server_image, (0,0))
                    await self.bot.say("Could not get the image, using defaults")


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

            result = Image.alpha_composite(result, process)

            result.save('data/drawing/temp.jpg','JPEG', quality=100)

            await self.bot.send_file(ctx.message.channel, 'data/drawing/temp.jpg')

            os.remove('data/drawing/temp.jpg')
            os.remove('data/drawing/temp_avatar')
            os.remove('data/drawing/temp_server')

        else:
            await self.bot.say("Couldn't get images")

    @commands.command(pass_context = True)
    async def rickroll(self, ctx):
        """Draws text on a background"""

        await self.bot.say("You asked for it. Prepare to sing along!")

        lyrics = [
            "Never gonna give you up",
            "Never gonna let you down",
            "Never gonna run around and desert you",
            "Never gonna make you cry",
            "Never gonna say goodbye",
            "Never gonna tell a lie and hurt you"
        ]

        def build_lyrics(source, text):
            source = copy(source)

            width = source.size[0]
            height = source.size[1]

            process = Image.new('RGBA', (width, height), (0,0,0))

            half_width = int(math.floor(width / 2))
            half_height = int(math.floor(height / 2))

            # get a font
            fnt_b = ImageFont.truetype('data/drawing/font_bold.ttf', 40)
            # get a drawing context
            d = ImageDraw.Draw(process)

            # haax
            d.rectangle([(0,0),(width,height)], fill=(0,0,0,0))

            # calculate position
            text_pos = int(math.floor(fnt_b.getsize(text)[0] / 2))

            # draw
            d.rectangle([(10, height - 70),(width - 10, height - 10)], fill=(0,0,0,160))
            d.text((half_width - text_pos, height - 55), text, font=fnt_b, fill=(255,255,255,255))

            return Image.alpha_composite(source, process)

        for line in enumerate(lyrics):
            if (line[0] + 1) % 3 == 0:
                result = Image.open('data/drawing/rr_3.jpg').convert('RGBA')
            elif (line[0] + 1) > 3:
                result = Image.open('data/drawing/rr_' + str(line[0] - 2) + '.png').convert('RGBA')
            else:
                result = Image.open('data/drawing/rr_' + str(line[0] + 1) + '.png').convert('RGBA')

            result = build_lyrics(result, line[1])

            result.save('temp.jpg','JPEG', quality=100)

            await self.bot.send_file(ctx.message.channel, 'temp.jpg')

            await asyncio.sleep(2)

            os.remove('temp.jpg')
        

def setup(bot):
    if pil_available is False:
        raise RuntimeError("You don't have Pillow installed, run\n```pip3 install pillow```And try again")
        return
    bot.add_cog(Drawing(bot))
