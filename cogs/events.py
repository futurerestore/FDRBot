from aioify import aioify
from discord.ext import commands
import aiosqlite
import discord
import os


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.os = aioify(os, name='os')
        self.utils = self.bot.get_cog('Utils')


    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild) -> None:
        await self.bot.wait_until_ready()

        async with aiosqlite.connect('Data/fdrbot.db') as db:
            async with db.execute('SELECT prefix from prefix WHERE guild = ?', (guild.id,)) as cursor:
                if await cursor.fetchone() is not None:
                    await db.execute('DELETE from prefix where guild = ?', (guild.id,))
                    await db.commit()

            await db.execute('INSERT INTO prefix(guild, prefix) VALUES(?,?)', (guild.id, '!'))
            await db.commit()


        embed = await self.utils.info_embed('!', self.bot.user)
        for channel in guild.text_channels:
            try:
                await channel.send(embed=embed)
                break
            except:
                pass

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild) -> None:
        await self.bot.wait_until_ready()

        async with aiosqlite.connect('Data/fdrbot.db') as db:
            await db.execute('DELETE from prefix where guild = ?', (guild.id,))
            await db.commit()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        await self.bot.wait_until_ready()

        if message.channel.type == discord.ChannelType.private:
            return

        if message.content.replace(' ', '').replace('!', '') == self.bot.user.mention:
            prefix = await self.utils.get_prefix(message.guild.id)

            embed = discord.Embed(title=self.bot.user.name, description=f'My prefix is `{prefix}`. To see all of my commands, run `{prefix}help`.')
            embed.set_footer(text=message.author.name, icon_url=message.author.avatar_url_as(static_format='png'))
            try:
                await message.reply(embed=embed)
            except:
                pass

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        await self.os.makedirs('Data', exist_ok=True)

        async with aiosqlite.connect('Data/fdrbot.db') as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS tags(
                name STRING,
                text STRING,
                creator INTEGER
                )
                ''')
            await db.commit()

            await db.execute('''
                CREATE TABLE IF NOT EXISTS prefix(
                guild INTEGER,
                prefix TEXT
                )
                ''')
            await db.commit()

        await self.bot.change_presence(activity=discord.Game(name='Ping me for help!'))
        print('FDRBot is now online.')

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error) -> None:
        await self.bot.wait_until_ready()

        if ctx.message.channel.type == discord.ChannelType.private:
            return

        embed = discord.Embed(title='Error')

        prefix = await self.utils.get_prefix(ctx.guild.id)
        if isinstance(error, commands.CommandNotFound):
            if ctx.prefix.replace('!', '').replace(' ', '') == self.bot.user.mention:
                return

            embed.description = f"That command doesn't exist! Use `{prefix}help` to see all the commands I can run."
            await ctx.reply(embed=embed)

        elif isinstance(error, commands.MaxConcurrencyReached):
            embed.description = f"`{prefix + ctx.command.qualified_name}` cannot be ran more than once at the same time!"
            await ctx.reply(embed=embed)

        elif isinstance(error, commands.errors.CommandInvokeError):
            if not isinstance(error.original, discord.errors.Forbidden):
                raise error

        elif isinstance(error, commands.ChannelNotFound):
            embed = discord.Embed(title='Error', description='That channel does not exist.')
            await ctx.reply(embed=embed)

        elif (isinstance(error, commands.errors.NotOwner)) or \
        (isinstance(error, commands.MissingPermissions)):
            return

        else:
            raise error


def setup(bot):
    bot.add_cog(Events(bot))
