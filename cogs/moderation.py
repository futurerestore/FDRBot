from datetime import datetime
from discord.commands import slash_command
from discord.ext import commands
from discord import Option

import asyncio
import discord


class ModCog(discord.Cog, name='Moderation'):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(description='Kick a user.')
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
        if not ctx.guild.me.guild_permissions.kick_members:
            raise commands.BotMissingPermissions(['kick_members'])

        if not ctx.author.guild_permissions.kick_members:
            raise commands.MissingPermissions(['kick_members'])

        try:
            member = await ctx.guild.fetch_member(user.id)
        except discord.HTTPException:
            raise commands.BadArgument(f'{user.mention} is not in this server.')

        if ctx.guild.roles.index(ctx.guild.me.top_role) <= ctx.guild.roles.index(
            member.top_role
        ):
            raise commands.BadArgument(
                f'I do not have permission to kick {member.mention}.'
            )

        if ctx.guild.roles.index(ctx.author.top_role) <= ctx.guild.roles.index(
            member.top_role
        ) or member in (ctx.author, ctx.guild.me, ctx.guild.owner):
            raise commands.BadArgument(f'You cannot kick {member.mention}.')

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

        async with self.bot.db.execute(
            'SELECT channel FROM logs WHERE guild = ?', (ctx.guild.id,)
        ) as cursor:
            data = await cursor.fetchone()

        if data is not None:
            channel = ctx.guild.get_channel(data[0])
            if channel is not None:
                embed = discord.Embed(
                    title='Member Kicked',
                    description=f"{member.mention} has been kicked by {ctx.author.mention}.",
                    timestamp=await asyncio.to_thread(datetime.now),
                )
                embed.set_thumbnail(url=member.avatar.with_static_format('png').url)
                embed.add_field(name='Member', value=member.mention)
                embed.add_field(name='Moderator', value=ctx.author.mention)
                if reason:
                    embed.add_field(name='Reason', value=reason, inline=False)

                await channel.send(embed=embed)
            else:
                await self.bot.db.execute(
                    'DELETE FROM logs WHERE guild = ?', (ctx.guild.id,)
                )
                await self.bot.db.commit()

    @slash_command(description='Ban a user.')
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
        if not ctx.guild.me.guild_permissions.ban_members:
            raise commands.BotMissingPermissions(['ban_members'])

        if not ctx.author.guild_permissions.ban_members:
            raise commands.MissingPermissions(['ban_members'])

        try:
            if ctx.guild.roles.index(ctx.guild.me.top_role) <= ctx.guild.roles.index(
                user.top_role
            ):
                raise commands.BadArgument(
                    f'I do not have permission to ban {user.mention}.'
                )

            user = await ctx.guild.fetch_member(user.id)
            if ctx.guild.roles.index(ctx.author.top_role) <= ctx.guild.roles.index(
                user.top_role
            ) or user in (ctx.author, ctx.guild.me, ctx.guild.owner):
                raise commands.BadArgument(f'You cannot ban {user.mention}.')

        except discord.HTTPException:
            pass

        if not 0 <= delete_messages <= 7:
            raise commands.BadArgument(
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

        async with self.bot.db.execute(
            'SELECT channel FROM logs WHERE guild = ?', (ctx.guild.id,)
        ) as cursor:
            data = await cursor.fetchone()

        if data is not None:
            channel = ctx.guild.get_channel(data[0])
            if channel is not None:
                embed = discord.Embed(
                    title='Member Banned',
                    description=f"{user.mention} has been Banned by {ctx.author.mention}.",
                    timestamp=await asyncio.to_thread(datetime.now),
                )
                embed.set_thumbnail(url=user.avatar.with_static_format('png').url)
                embed.add_field(name='Member', value=user.mention)
                embed.add_field(name='Moderator', value=ctx.author.mention)
                if reason:
                    embed.add_field(name='Reason', value=reason, inline=False)

                await channel.send(embed=embed)
            else:
                await self.bot.db.execute(
                    'DELETE FROM logs WHERE guild = ?', (ctx.guild.id,)
                )
                await self.bot.db.commit()

    @slash_command(
        name='modchannel', description='Set channel to send moderation actions to.'
    )
    async def set_modchannel(
        self,
        ctx: discord.ApplicationContext,
        channel: Option(
            discord.TextChannel, description='Channel to send moderation actions to.'
        ),
    ) -> None:
        if not channel.permissions_for(ctx.guild.me).send_messages:
            raise commands.BadArgument(
                f'I do not have permission to send messages in {channel.mention}.'
            )

        if not ctx.author.guild_permissions.manage_guild:
            raise commands.MissingPermissions(['manage_guild'])

        await self.bot.db.execute(
            'INSERT INTO logs(guild, channel) VALUES(?,?)',
            (ctx.guild.id, channel.id),
        )
        await self.bot.db.commit()

        embed = discord.Embed(
            title='Moderation Logs',
            description=f'Moderation actions will now be sent to {channel.mention}.',
        )
        embed.set_footer(
            text=ctx.author.display_name,
            icon_url=ctx.author.avatar.with_static_format('png').url,
        )
        await ctx.respond(embed=embed, ephemeral=True)

    @slash_command(description='Delete messages from a channel.')
    async def clear(
        self,
        ctx: discord.ApplicationContext,
        messages: Option(int, description='Number of messages to delete.'),
    ) -> None:
        for perm in ('manage_messages', 'read_message_history'):
            if not getattr(ctx.guild.me.guild_permissions, perm):
                raise commands.BotMissingPermissions([perm])

        if not ctx.author.guild_permissions.manage_messages:
            raise commands.MissingPermissions(['manage_messages'])

        if messages == 0:
            raise commands.BadArgument(
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


def setup(bot: discord.Bot):
    bot.add_cog(ModCog(bot))
