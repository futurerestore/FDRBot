from discord.commands import slash_command
from datetime import datetime

import asyncio
import discord
import sys


class MiscCog(discord.Cog, name='Miscellaneous'):
    def __init__(self, bot):
        self.bot = bot
        self.utils = self.bot.get_cog('Utilities')

    @slash_command(description="See FDRBot's latency.")
    async def ping(self, ctx: discord.ApplicationContext) -> None:
        embed = discord.Embed(title='Pong!', description='Testing ping...')
        embed.set_thumbnail(
            url=self.bot.user.display_avatar.with_static_format('png').url
        )
        embed.set_footer(
            text=ctx.author.name,
            icon_url=ctx.author.display_avatar.with_static_format('png').url,
        )

        current_time = await asyncio.to_thread(datetime.utcnow)
        await ctx.respond(embed=embed, ephemeral=True)

        embed.description = f'API ping: `{round(self.bot.latency * 1000)}ms`\nMessage Ping: `{round((await asyncio.to_thread(datetime.utcnow) - current_time).total_seconds() * 1000)}ms`'
        await ctx.edit(embed=embed)

    @slash_command(description="See FDRBot's statistics.")
    async def stats(self, ctx: discord.ApplicationContext) -> None:
        async with self.bot.db.execute('SELECT start_time from uptime') as cursor:
            start_time = (await cursor.fetchone())[0]

        embed = {
            'title': 'FDRBot Statistics',
            'fields': [
                {
                    'name': 'Bot Started',
                    'value': await self.utils.get_uptime(start_time),
                    'inline': True,
                },
                {
                    'name': 'Python Version',
                    'value': '.'.join(
                        str(_)
                        for _ in (
                            sys.version_info.major,
                            sys.version_info.minor,
                            sys.version_info.micro,
                        )
                    ),
                    'inline': True,
                },
            ],
            'footer': {
                'text': ctx.author.display_name,
                'icon_url': str(
                    ctx.author.display_avatar.with_static_format('png').url
                ),
            },
        }

        await ctx.respond(embed=discord.Embed.from_dict(embed), ephemeral=True)


def setup(bot: discord.Bot):
    bot.add_cog(MiscCog(bot))
