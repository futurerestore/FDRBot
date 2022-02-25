from datetime import datetime
from discord.enums import SlashCommandOptionType

import discord


class UtilsCog(discord.Cog, name='Utilities'):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    READABLE_INPUT_TYPES = {
        SlashCommandOptionType.string: 'string',
        SlashCommandOptionType.channel: 'channel',
        SlashCommandOptionType.user: 'user',
    }

    async def get_uptime(self, time: int) -> str:
        start_time = datetime.fromtimestamp(time)

        return discord.utils.format_dt(start_time, style='R')

    # HelpCog helper functions
    async def cmd_help_embed(
        self, ctx: discord.ApplicationContext, cmd: discord.SlashCommand
    ):
        embed = {
            'title': f"/{' '.join((cmd.full_parent_name, cmd.name)) or cmd.name} ",
            'description': cmd.description,
            'fields': list(),
            'footer': {
                'text': ctx.author.display_name,
                'icon_url': str(
                    ctx.author.display_avatar.with_static_format('png').url
                ),
            },
        }

        for arg in cmd.options:
            embed['title'] += f'<{arg.name}> ' if arg.required else f'[{arg.name}] '
            embed['fields'].append(
                {
                    'name': f'<{arg.name}>' if arg.required else f'[{arg.name}]',
                    'value': f"```Description: {arg.description or 'No description'}\nInput Type: {self.READABLE_INPUT_TYPES[arg.input_type]}\nRequired: {arg.required}```",
                    'inline': True,
                }
            )

        return discord.Embed.from_dict(embed)

    async def cog_help_embed(
        self, ctx: discord.ApplicationContext, cog: str
    ) -> list[discord.Embed]:
        embed = {
            'title': f"{cog.capitalize() if cog != 'tss' else cog.upper()} Commands",
            'fields': list(),
            'footer': {
                'text': ctx.author.display_name,
                'icon_url': str(
                    ctx.author.display_avatar.with_static_format('png').url
                ),
            },
        }

        for cmd in self.bot.cogs[cog].get_commands():
            if isinstance(cmd, discord.SlashCommandGroup):
                continue

            cmd_field = {
                'name': f"/{cmd.name} ",
                'value': cmd.description,
                'inline': False,
            }

            for arg in cmd.options:
                cmd_field['name'] += (
                    f'<{arg.name}> ' if arg.required else f'[{arg.name}] '
                )

            embed['fields'].append(cmd_field)

        embed['fields'] = sorted(embed['fields'], key=lambda field: field['name'])
        return discord.Embed.from_dict(embed)

    async def group_help_embed(
        self, ctx: discord.ApplicationContext, group: discord.SlashCommandGroup
    ) -> list[discord.Embed]:
        embed = {
            'title': f"{group.name.capitalize() if group.name != 'tss' else group.name.upper()} Commands",
            'fields': list(),
            'footer': {
                'text': ctx.author.display_name,
                'icon_url': str(
                    ctx.author.display_avatar.with_static_format('png').url
                ),
            },
        }

        for cmd in group.subcommands:
            cmd_field = {
                'name': f"/{' '.join((group.name, cmd.name))} ",
                'value': cmd.description,
                'inline': False,
            }
            for arg in cmd.options:
                cmd_field['name'] += (
                    f'<{arg.name}> ' if arg.required else f'[{arg.name}] '
                )

            embed['fields'].append(cmd_field)

        embed['fields'] = sorted(embed['fields'], key=lambda field: field['name'])
        return discord.Embed.from_dict(embed)


def setup(bot):
    bot.add_cog(UtilsCog(bot))
