from discord.ext import commands

import discord


class EventsCog(discord.Cog, name='Events'):
    def __init__(self, bot):
        self.bot = bot

    @discord.Cog.listener()
    async def on_ready(self) -> None:
        print('FDRBot is now online.')

    @discord.Cog.listener()
    async def on_application_command_error(
        self, ctx: discord.ApplicationContext, exc: commands.errors.CommandError
    ) -> None:
        await self.bot.wait_until_ready()

        if isinstance(exc, discord.ApplicationCommandInvokeError):
            exc = exc.__cause__

        embed = discord.Embed(title='Error')
        if isinstance(exc, commands.errors.NoPrivateMessage):
            embed.description = 'This command can only be used in a server.'

        elif isinstance(
            exc,
            (commands.errors.MissingPermissions, commands.errors.BotMissingPermissions),
        ):
            missing_perms = [
                perm.replace('_', ' ').replace('guild', 'server').title()
                for perm in exc.missing_permissions
            ]

            if len(missing_perms) > 2:
                fmt = '{}, and {}'.format(
                    ", ".join(missing_perms[:-1]), missing_perms[-1]
                )
            else:
                fmt = ' and '.join(missing_perms)

            if isinstance(exc, commands.errors.MissingPermissions):
                embed.description = f'You are missing the following permissions required to run this command: {fmt}.'
            elif isinstance(exc, commands.errors.BotMissingPermissions):
                embed.description = f'I am missing the following permissions required to run this command: {fmt}.'

        elif isinstance(exc, commands.errors.BadArgument):
            embed.description = str(exc)

        elif isinstance(exc, commands.errors.UserNotFound):
            embed.description = 'I could not find that user.'

        else:
            owner = await self.bot.fetch_user(self.bot.owner_id)
            embed.description = (
                f'An unknown error occurred, please report this to {owner.mention}!'
            )
            embed.add_field(
                name='Error Info',
                value=f'Command: `/{ctx.command.qualified_name}`\nError message: `{str(exc)}`',
            )

        if not ctx.interaction.response.is_done():
            await ctx.respond(embed=embed, ephemeral=True)
        else:
            await ctx.edit(embed=embed)


def setup(bot):
    bot.add_cog(EventsCog(bot))
