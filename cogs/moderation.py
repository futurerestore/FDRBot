from discord.ext import commands
from typing import Union
import discord


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    @commands.has_guild_permissions(kick_members=True)
    async def kick(self, ctx: commands.Context, user: Union[discord.Member, int], *, reason: str=None) -> None:
        if isinstance(user, int):
            user = ctx.guild.get_member(user)

        embed = discord.Embed(title='Error')

        if user is None:
            embed.description = "This member doesn't exist!"  
            await ctx.reply(embed=embed)
            return

        elif user == ctx.author:
            return

        if ctx.guild.roles.index(ctx.author.top_role) <= ctx.guild.roles.index(user.top_role):
            embed.description = f"You don't have permission to kick {user.mention}!"
            await ctx.reply(embed=embed)
            return

        if ctx.guild.roles.index(ctx.guild.me.top_role) <= ctx.guild.roles.index(user.top_role):
            embed.description = f"I don't have permission to kick {user.mention}!"
            await ctx.reply(embed=embed)
            return

        embed.title = 'Kick'

        try:
            embed.description = f"You've been kicked from **{ctx.guild.name}**{f' for `{reason}`' if reason else ''}."
            embed.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar_url_as(static_format='png'))
            await user.send(embed=embed)

        except discord.errors.HTTPException:
            pass

        await user.kick(reason=reason)

        embed.description = f"{user.mention} has been kicked{f' for `{reason}`.' if reason else '.'}"
        embed.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url_as(static_format='png'))
        await ctx.reply(embed=embed)

    @commands.command()
    @commands.guild_only()
    @commands.has_guild_permissions(ban_members=True)
    async def ban(self, ctx: commands.Context, user: Union[discord.Member, discord.User, int], *, reason: str=None) -> None:
        if isinstance(user, int):
            user = ctx.guild.get_member(user)

        embed = discord.Embed(title='Error')

        if user is None:
            embed.description = "This member doesn't exist!"  
            await ctx.reply(embed=embed)
            return

        if user in [m for r, m in await ctx.guild.bans()]:
            embed.description = 'This member is already banned!'
            await ctx.reply(embed=embed)
            return

        elif user == ctx.author:
            return

        if isinstance(user, discord.Member):
            if ctx.guild.roles.index(ctx.author.top_role) <= ctx.guild.roles.index(user.top_role):
                embed.description = f"You don't have permission to ban {user.mention}!"
                await ctx.reply(embed=embed)
                return

            if ctx.guild.roles.index(ctx.guild.me.top_role) <= ctx.guild.roles.index(user.top_role):
                embed.description = f"I don't have permission to ban {user.mention}!"
                await ctx.reply(embed=embed)
                return

        embed.title = 'Ban'

        try:
            embed.description = f"You've been banned from **{ctx.guild.name}**{f' for `{reason}`' if reason else ''}."
            embed.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar_url_as(static_format='png'))
            await user.send(embed=embed)

        except discord.errors.HTTPException:
            pass

        if isinstance(user, discord.User):
            await ctx.guild.ban(discord.Object(id=user.id), reason=reason)
        else:
            await user.ban(reason=reason)

        embed.description = f"{user.mention} has been banned{f' for `{reason}`.' if reason else '.'}"
        embed.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url_as(static_format='png'))

        await ctx.reply(embed=embed)

    @commands.command()
    @commands.guild_only()
    @commands.has_guild_permissions(ban_members=True)
    async def unban(self, ctx: commands.Context, user: Union[discord.User, int]) -> None:
        if isinstance(user, int):
            user = await self.bot.fetch_user(user)

        embed = discord.Embed(title='Error')

        if user is None:
            embed.description = "This member doesn't exist!"  
            await ctx.reply(embed=embed)
            return

        elif user == ctx.author:
            return

        elif user not in [m for r, m in await ctx.guild.bans()]:
            embed.description = 'This member is not banned!'
            await ctx.reply(embed=embed)
            return

        embed.title = 'Unban'

        try:
            embed.description = f"You've been unbanned from **{ctx.guild.name}**."
            embed.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar_url_as(static_format='png'))
            await user.send(embed=embed)

        except discord.errors.HTTPException:
            pass

        await ctx.guild.unban(user)

        embed.description = f"{user.mention} has been unbanned."
        embed.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url_as(static_format='png'))
        await ctx.reply(embed=embed)

    @commands.command(aliases=('purge',))
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx: commands.Context, num: int) -> None:
        await ctx.message.delete()
        await ctx.channel.purge(limit=num)

        embed = discord.Embed(title='Clear', description=f"`{num}` message{'s' if num != 1 else ''} deleted.")
        embed.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url_as(static_format='png'))
        message = await ctx.send(embed=embed)
        await message.delete(delay=3)


def setup(bot):
    bot.add_cog(Moderation(bot))
