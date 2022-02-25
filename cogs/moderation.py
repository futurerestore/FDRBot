from discord.commands import slash_command
from discord.ext import commands
from discord import Option

import discord


class ModerationCog(discord.Cog, name='Moderation'):
    def __init__(self, bot):
        self.bot = bot

    @slash_command()
    async def kick(
        self,
        ctx: discord.ApplicationContext,
        user: Option(commands.UserConverter, description='User to kick.'),
        reason: Option(
            str,
            description='Reason for kicking the user.',
            required=False,
        ),
    ) -> None:
        if ctx.guild is None:
            raise commands.errors.NoPrivateMessage()

        if not ctx.guild.me.guild_permissions.kick_members:
            raise commands.errors.BotMissingPermissions(['kick_members'])

        if not ctx.author.guild_permissions.kick_members:
            raise commands.errors.MissingPermissions(['kick_members'])

        member = ctx.guild.get_member(user.id)
        if member is None:
            raise commands.errors.BadArgument(f'{user.mention} is not in this server.')

        if ctx.guild.roles.index(ctx.guild.me.top_role) <= ctx.guild.roles.index(
            member.top_role
        ):
            raise commands.errors.BadArgument(
                f'I do not have permission to kick {member.mention}.'
            )

        if ctx.guild.roles.index(ctx.author.top_role) <= ctx.guild.roles.index(
            member.top_role
        ) or member in (ctx.author, ctx.guild.me, ctx.guild.owner):
            raise commands.errors.BadArgument(f'You cannot kick {member.mention}.')

        embed = discord.Embed(
            title='Kick',
            description=f"You've been kicked from **{ctx.guild.name}** by {ctx.author.mention}{f' for `{reason}`' if reason else ''}.",
        )
        embed.set_footer(
            text=self.bot.user.name,
            icon_url=self.bot.user.avatar.with_static_format('png').url,
        )

        try:
            await member.send(embed=embed)
        except discord.errors.HTTPException:
            pass

        await member.kick(reason=reason)

        embed.description = (
            f"{member.mention} has been kicked{f' for `{reason}`.' if reason else '.'}"
        )
        embed.set_footer(
            text=ctx.author.display_name,
            icon_url=ctx.author.avatar.with_static_format('png').url,
        )
        await ctx.respond(embed=embed)

    @slash_command()
    async def ban(
        self,
        ctx: discord.ApplicationContext,
        user: Option(commands.UserConverter, description='User to ban.'),
        reason: Option(
            str,
            description='Reason for banning the user.',
            required=False,
        ),
        delete_messages: Option(
            int,
            description='Days of message history to delete (defaults to 0).',
            default=0,
        ),
    ) -> None:
        if ctx.guild is None:
            raise commands.errors.NoPrivateMessage()

        if not ctx.guild.me.guild_permissions.ban_members:
            raise commands.errors.BotMissingPermissions(['ban_members'])

        if not ctx.author.guild_permissions.ban_members:
            raise commands.errors.MissingPermissions(['ban_members'])

        if ctx.guild.roles.index(ctx.guild.me.top_role) <= ctx.guild.roles.index(
            user.top_role
        ):
            raise commands.errors.BadArgument(
                f'I do not have permission to ban {user.mention}.'
            )

        if ctx.guild.roles.index(ctx.author.top_role) <= ctx.guild.roles.index(
            user.top_role
        ) or user in (ctx.author, ctx.guild.me, ctx.guild.owner):
            raise commands.errors.BadArgument(f'You cannot ban {user.mention}.')

        if not 0 <= delete_messages <= 7:
            raise commands.errors.BadArgument(
                'Number of days of message history to delete must be between 0-7.'
            )

        embed = discord.Embed(
            title='Ban',
            description=f"You've been banned from **{ctx.guild.name}** by {ctx.author.mention}{f' for `{reason}`' if reason else ''}.",
        )
        embed.set_footer(
            text=self.bot.user.name,
            icon_url=self.bot.user.avatar.with_static_format('png').url,
        )

        try:
            await user.send(embed=embed)
        except discord.errors.HTTPException:
            pass

        await ctx.guild.ban(user, reason=reason, delete_messages=delete_messages)

        embed.description = (
            f"{user.mention} has been banned{f' for `{reason}`.' if reason else '.'}"
        )
        embed.set_footer(
            text=ctx.author.display_name,
            icon_url=ctx.author.avatar.with_static_format('png').url,
        )
        await ctx.respond(embed=embed)

    @slash_command()
    async def clear(
        self,
        ctx: discord.ApplicationContext,
        messages: Option(int, description='Number of messages to delete.'),
    ) -> None:
        if ctx.guild is None:
            raise commands.errors.NoPrivateMessage()

        for perm in ('manage_messages', 'read_message_history'):
            if not getattr(ctx.guild.me.guild_permissions, perm):
                raise commands.errors.BotMissingPermissions([perm])

        if not ctx.author.guild_permissions.manage_messages:
            raise commands.errors.MissingPermissions(['manage_messages'])

        if messages == 0:
            raise commands.errors.BadArgument(
                'Number of messages to delete must be greater than 0.'
            )

        await ctx.channel.purge(limit=messages)

        embed = discord.Embed(
            title='Clear',
            description=f"**{messages} **message{'s' if messages != 1 else ''}** deleted.",
        )
        embed.set_footer(
            text=ctx.author.display_name,
            icon_url=ctx.author.avatar.with_static_format('png').url,
        )
        await ctx.respond(embed=embed, delete_after=5)


def setup(bot):
    bot.add_cog(ModerationCog(bot))
