from discord.ext import commands
import discord


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.utils = self.bot.get_cog('Utils')

    @commands.group(name='help', invoke_without_command=True)
    @commands.guild_only()
    async def help_command(self, ctx: commands.Context) -> None:
        prefix = await self.utils.get_prefix(ctx.guild.id)

        embed = discord.Embed(title='Commands')
        if await ctx.bot.is_owner(ctx.author):
            embed.add_field(name='Admin Commands', value=f'`{prefix}help admin`', inline=False)
        embed.add_field(name='Miscellaneous Commands', value=f'`{prefix}help misc`', inline=False)
        embed.add_field(name='Tag Commands', value=f'`{prefix}help tag`', inline=False)

        embed.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url_as(static_format='png'))
        await ctx.reply(embed=embed)

    @help_command.command(name='admin')
    @commands.guild_only()
    @commands.is_owner()
    async def admin_commands(self, ctx: commands.Context) -> None:
        prefix = await self.utils.get_prefix(ctx.guild.id)

        embed = discord.Embed(title='Admin Commands')
        embed.add_field(name='See module subcommands', value=f'`{prefix}module`', inline=False)

        embed.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url_as(static_format='png'))
        await ctx.reply(embed=embed)

    @help_command.command(name='misc')
    @commands.guild_only()
    @commands.is_owner()
    async def misc_commands(self, ctx: commands.Context) -> None:
        prefix = await self.utils.get_prefix(ctx.guild.id)

        embed = discord.Embed(title='Miscellaneous Commands')
        embed.add_field(name='Get bot latency', value=f'`{prefix}ping`', inline=False)
        if ctx.author.guild_permissions.administrator:
            embed.add_field(name='Set prefix', value=f'`{prefix}prefix`', inline=False)

        embed.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url_as(static_format='png'))
        await ctx.reply(embed=embed)


    @help_command.command(name='tag')
    @commands.guild_only()
    @commands.is_owner()
    async def tag_commands(self, ctx: commands.Context) -> None:
        prefix = await self.utils.get_prefix(ctx.guild.id)

        embed = discord.Embed(title='Tag Commands')
        embed.add_field(name='Send tag', value=f'`{prefix}tag <tag>`', inline=False)
        embed.add_field(name='See all tags', value=f'`{prefix}taglist`', inline=False)
        if ctx.author.guild_permissions.manage_messages:
            embed.add_field(name='Add tag', value=f'`{prefix}addtag <tag>`', inline=False)
            embed.add_field(name='Remove tag', value=f'`{prefix}deltag <tag>`', inline=False)

        embed.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url_as(static_format='png'))
        await ctx.reply(embed=embed)


def setup(bot):
    bot.add_cog(Help(bot))
