import discord
from discord.ext import commands
from .utils import checks
import aiohttp
import json
import logging
import time
import os

log = logging.getLogger('red.apitools')


class Apitools:
    """Steam and SteamSpy related commands"""
    def __init__(self, bot):
        self.bot = bot

    @commands.group(pass_context=True, name='apitools', aliases=['api'])
    async def apitools(self, ctx):

        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)


    # Parsing functions
    def _parse_headers(self, answer):
        headers = {}
        public_headers = {}

        if answer is not None and answer.content.strip() != 'pass':
            for line in answer.content.splitlines():
                header = line.strip().split('=')
                public_header = False

                if len(header) == 2:

                    # check for env vars
                    if '$ENV' in header[1]:
                        varname = header[1][header[1].index('$ENV') + 5:-1]
                        try:
                            header[1] = os.environ[varname]
                            public_header = 'secret'
                        except:
                            public_header = 'ENV var parsing failed'

                    headers[header[0]] = header[1]
                    public_headers[header[0]] = public_header or header[1]

        return {'headers': headers, 'public_headers': public_headers}

    def _parse_body(self, answer):
        body = {}
        if answer is not None and answer.content.strip() != 'pass':
            for line in answer.content.splitlines():
                body_item = line.strip().split('=')
                if len(body_item) == 2:
                    body[body_item[0]] = body_item[1]

        return body


    @checks.is_owner()
    @apitools.command(pass_context=True, name='get')
    async def _get(self, ctx, url, w_headers=False):
        """Shows estimated amount of owners for the game"""

        url = url.strip()

        if w_headers:
            await self.bot.say('Set headers by typing them in a `name=value` format, one on each line, or `pass`')

            answer = await self.bot.wait_for_message(timeout=50, author=ctx.message.author)

            parsed = self._parse_headers(answer)
            headers = parsed['headers']
            public_headers = parsed['public_headers']

            await self.bot.say(
                'Headers are set to:\n```json\n{}```'.format(json.dumps(public_headers, indent=4, sort_keys=True)))

        else:
            headers = {}

        t1 = time.perf_counter()
        async with aiohttp.get(url, headers=headers) as r:
            t2 = time.perf_counter()
            data = await r.text()
            status = r.status

        try:
            parsed = json.loads(data)
        except:
            parsed = json.loads('{}')


        color = status == 200 and 0x2ecc71 or status >= 400 and 0xe74c3c
        embed = discord.Embed(title='Results for **GET** {}'.format(url),
                              color=color,
                              description='```json\n{}```'.format(len(data) < 700
                                                                  and
                                                                  json.dumps(parsed, indent=4, sort_keys=True)
                                                                  or
                                                                  json.dumps(parsed, indent=4, sort_keys=True)[:700]
                                                                  + '\n\n...\n\n'))
        embed.add_field(name='Status',
                        value=status)
        embed.add_field(name='Time',
                        value='{}ms'.format(str((t2-t1) * 1000)[:3]))
        await self.bot.say(embed=embed)

    @checks.is_owner()
    @apitools.command(pass_context=True, name='post', aliases=['put'])
    async def _post(self, ctx, *, url):
        """Shows estimated amount of owners for the game"""

        await self.bot.say('Set headers by typing them in a `name=value` format, one on each line, or `pass`')

        answer = await self.bot.wait_for_message(timeout=50, author=ctx.message.author)

        parsed = self._parse_headers(answer)
        headers = parsed['headers']
        public_headers = parsed['public_headers']

        await self.bot.say('Headers are set to:\n```json\n{}```\nSet body typing in in a `name=value` one on each line or `pass`\nNested objects are not supported'
                           .format(json.dumps(public_headers, indent=4, sort_keys=True)))

        answer = await self.bot.wait_for_message(timeout=50, author=ctx.message.author)

        body = self._parse_body(answer)

        await self.bot.say('Body is set to:\n```json\n{}```'.format(json.dumps(body, indent=4, sort_keys=True)))

        url = url.strip()
        method = ctx.invoked_with

        if method == 'post':
            t1 = time.perf_counter()
            async with aiohttp.post(url, headers=headers, data=json.dumps(body)) as r:
                t2 = time.perf_counter()
                data = await r.text()
                status = r.status

        if method == 'put':
            if 'Content-Type' not in headers:
                headers['Content-Type'] = 'application/json'

            t1 = time.perf_counter()
            async with aiohttp.put(url, headers=headers, data=json.dumps(body)) as r:
                t2 = time.perf_counter()
                data = await r.text()
                status = r.status

        try:
            parsed = json.loads(data)
        except:
            parsed = json.loads('{}')

        color = status == 200 and 0x2ecc71 or status >= 400 and 0xe74c3c
        embed = discord.Embed(title='Results for **{}** {}'.format(method.upper(), url),
                              color=color,
                              description='```json\n{}```'.format(len(data) < 700
                                                                  and
                                                                  json.dumps(parsed, indent=4, sort_keys=True)
                                                                  or
                                                                  json.dumps(parsed, indent=4, sort_keys=True)[:700]
                                                                  + '\n\n...\n\n'))
        embed.add_field(name='Status',
                        value=status)
        embed.add_field(name='Time',
                        value='{}ms'.format(str((t2-t1) * 1000)[:3]))
        await self.bot.say(embed=embed)


def setup(bot):
    bot.add_cog(Apitools(bot))
