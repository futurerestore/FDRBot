from discord.ext import commands
import aiosqlite
import asyncio
import discord


class Tags(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=('t',))
    @commands.guild_only()
    async def tag(self, ctx: commands.Context, tag: str) -> None:
        async with aiosqlite.connect('Data/fdrbot.db') as db, db.execute('SELECT * FROM tags WHERE name = ?', (tag,)) as cursor:
            tag = await cursor.fetchone()

        if tag is None:
            embed = discord.Embed(title='Error', description="That tag doesn't exist!")
            await ctx.reply(embed=embed)
            return

        creator = await self.bot.fetch_user(tag[2])
        if creator is None:
            name = 'Deleted User'
        else:
            name = f'{creator.name}#{creator.discriminator}'

        embed = discord.Embed(title=tag[0], description=tag[1])
        embed.set_footer(text=f'Created by {name}')
        if ctx.message.reference:
            try:
                await ctx.message.reference.cached_message.reply(embed=embed)
                return
            except:
                pass

        await ctx.reply(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def addtag(self, ctx: commands.Context, name: str) -> None:
        cancelled_embed = discord.Embed(title='Add Tag', description='Cancelled.')
        embed = discord.Embed(title='Add Tag', description=f'What text would you like to have for `{name}`? Type `cancel` to cancel.')
        timeout_embed = discord.Embed(title='Add Tag', description='No response given in 5 minutes, cancelling.')

        for x in (embed, cancelled_embed, timeout_embed):
            x.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url_as(static_format='png'))

        async with aiosqlite.connect('Data/fdrbot.db') as db, db.execute('SELECT FROM tags WHERE name = ?', (name,)) as cursor:
            tag = await cursor.fetchone()
    
        if tag is not None:
            embed = discord.Embed(title='Error', description=f'A tag with the name {name} already exists!')
            await ctx.reply(embed=embed)
            return

        message = await ctx.reply(embed=embed)

        try:
            response = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=300)
            answer = response.content
        except asyncio.exceptions.TimeoutError:
            await message.edit(embed=timeout_embed)
            return

        try:
            await response.delete()
        except discord.errors.NotFound:
            pass

        if answer.lower().replace(' ', '') == 'cancel':
            await message.edit(embed=cancelled_embed)
            return

        async with aiosqlite.connect('Data/fdrbot.db') as db:
            await db.execute('INSERT INTO tags(name, text, creator) VALUES(?,?,?)', (name, answer, ctx.author.id))
            await db.commit()

        embed = discord.Embed(title='Add Tag', description=f'`{name}` tag added!')
        embed.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url_as(static_format='png'))
        await message.edit(embed=embed)


    @commands.command(aliases=('rmtag', 'deletetag'))
    @commands.guild_only()
    async def deltag(self, ctx: commands.Context, name: str) -> None:
        cancelled_embed = discord.Embed(title='Remove Tag', description='Cancelled.')
        invalid_embed = discord.Embed(title='Remove Tag', description='This tag does not exist!')
        timeout_embed = discord.Embed(title='Remove Tag', description='No response given in 5 minutes, cancelling.')
        embed = discord.Embed(title='Remove Tag', description=f"Are you sure you'd like to delete `{name}`? Type `yes` to remove this tag, or anything else to cancel.")

        for x in (embed, cancelled_embed, invalid_embed, timeout_embed):
            x.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url_as(static_format='png'))

        async with aiosqlite.connect('Data/fdrbot.db') as db, db.execute('SELECT * FROM tags WHERE name = ?', (name,)) as cursor:
            tag = await cursor.fetchone()

        if tag is None:
            await ctx.reply(invalid_embed)
            return

        message = await ctx.reply(embed=embed)

        try:
            response = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=300)
            answer = response.content.lower()
        except asyncio.exceptions.TimeoutError:
            await message.edit(embed=timeout_embed)
            return

        try:
            await response.delete()
        except discord.errors.NotFound:
            pass

        if 'yes' not in answer:
            await message.edit(embed=cancelled_embed)
            return

        async with aiosqlite.connect('Data/fdrbot.db') as db:
            await db.execute('DELETE FROM tags WHERE name = ?', (name,))
            await db.commit()

        embed = discord.Embed(title='Remove Tag', description=f'`{name}` tag removed!')
        embed.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url_as(static_format='png'))
        await message.edit(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def taglist(self, ctx: commands.Context) -> None:
        async with aiosqlite.connect('Data/fdrbot.db') as db, db.execute('SELECT name, creator FROM tags') as cursor:
            tags = await cursor.fetchall()

        if tags is None or len(tags) == 0:
            embed = discord.Embed(title='Error', description="There aren't any tags!")
            await ctx.reply(embed=embed)
            return

        embed = discord.Embed(title='Tags')
        for tag in tags:
            creator = await self.bot.fetch_user(tag[1])
            if creator is None:
                mention = 'Deleted User'
            else:
                mention = creator.mention

            embed.add_field(name=tag[0], value=f'**Creator:** {mention}')

        embed.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url_as(static_format='png'))
        await ctx.reply(embed=embed)

def setup(bot):
    bot.add_cog(Tags(bot))
