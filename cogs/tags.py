from collections import namedtuple
from discord.commands import SlashCommandGroup, slash_command
from discord.enums import InputTextStyle
from discord.ext import commands
from discord.ui import InputText
from discord import Option
from utils.errors import *
from utils.views.modals import QuestionModal
from utils.views.buttons import PaginatorView, SelectView

import discord


TagData = namedtuple('TagData', ['name', 'content', 'uses', 'creator'])


async def tag_autocomplete(ctx: discord.AutocompleteContext):
    res = list()
    async with ctx.bot.db.execute('SELECT name FROM tags') as cursor:
        for row in await cursor.fetchall():
            if ctx.value.lower() in row[0]:
                res.append(row[0])

    res.sort()
    return res


class TagsCog(discord.Cog, name='Tags'):
    def __init__(self, bot):
        self.bot = bot

    tags = SlashCommandGroup('tags', 'Tag commands')

    @slash_command(name='tag', description='Display a tag.')
    async def _tag(
        self,
        ctx: discord.ApplicationContext,
        name: Option(str, description='Name of tag.', autocomplete=tag_autocomplete),
    ) -> None:
        await self.bot.db.execute(
            'UPDATE tags SET uses = uses + 1 WHERE name = ?', (name,)
        )
        await self.bot.db.commit()

        async with self.bot.db.execute(
            'SELECT * FROM tags WHERE name = ?', (name,)
        ) as cursor:
            data = await cursor.fetchone()

        if data is None:
            raise commands.BadArgument('Tag not found.')

        tag = TagData(*data)
        try:
            creator = await self.bot.fetch_user(tag.creator)
            name = f'{creator.name}#{creator.discriminator}'
        except discord.errors.NotFound:
            name = 'Deleted User'

        embed = discord.Embed(title=tag.name, description=tag.content)
        embed.set_footer(
            text=f"Created by {name} | Used {tag.uses} time{'s' if tag.uses != 1 else ''}"
        )

        await ctx.respond(embed=embed)

    @tags.command(name='add', description='Create a tag.')
    async def add_tag(self, ctx: discord.ApplicationContext) -> None:
        if not ctx.author.guild_permissions.manage_messages:
            raise commands.MissingPermissions(['manage_messages'])

        embed = discord.Embed(title='Add Tag', description='Adding tag...')
        embed.set_footer(
            text=ctx.author.display_name,
            icon_url=ctx.author.avatar.with_static_format('png').url,
        )

        modal = QuestionModal(
            ctx,
            'Add Tag',
            embed,
            InputText(label='Enter a name for the tag.'),
            InputText(label='Enter the content of the tag.', style=InputTextStyle.long),
        )

        await ctx.interaction.response.send_modal(modal)
        await modal.wait()

        tag = TagData(modal.answers[0].lower(), modal.answers[1], 0, ctx.author.id)
        if len(tag.name.split()) > 1:
            raise commands.BadArgument('Tag names can only be one word.')

        async with self.bot.db.execute(
            'SELECT * FROM tags WHERE name = ?', (tag.name,)
        ) as cursor:
            if await cursor.fetchone() is not None:
                raise commands.BadArgument(
                    f'A tag with the name `{tag.name}` already exists.'
                )

        await self.bot.db.execute(
            'INSERT INTO tags(name, content, uses, creator) VALUES(?,?,?,?)',
            [*tag],
        )
        await self.bot.db.commit()

        embed = discord.Embed(title='Add Tag', description=f'`{tag.name}` tag added!')
        embed.set_footer(
            text=ctx.author.display_name,
            icon_url=ctx.author.avatar.with_static_format('png').url,
        )
        await ctx.edit(embed=embed)

    @tags.command(name='remove', description='Remove a tag.')
    async def rm_tag(
        self,
        ctx: discord.ApplicationContext,
        name: Option(
            str, description='Name of tag to remove.', autocomplete=tag_autocomplete
        ),
    ) -> None:
        async with self.bot.db.execute(
            'SELECT * FROM tags WHERE name = ?', (name,)
        ) as cursor:
            data = await cursor.fetchone()

        if data is None:
            raise commands.BadArgument(f'Tag `{name}` not found.')

        embed = discord.Embed(
            title='Remove Tag',
            description=f"Are you sure you'd like to remove the `{name}` tag?",
        )
        embed.set_footer(
            text=ctx.author.display_name,
            icon_url=ctx.author.display_avatar.with_static_format('png').url,
        )

        buttons = [
            {'label': 'Confirm', 'style': discord.ButtonStyle.danger},
            {'label': 'Cancel', 'style': discord.ButtonStyle.secondary},
        ]

        view = SelectView(buttons, ctx)
        await ctx.respond(embed=embed, view=view, ephemeral=True)
        await view.wait()
        if view.answer is None:
            raise ViewTimeoutException(view.timeout)

        if view.answer == 'Cancel':
            embed.description = 'Cancelled.'
            await ctx.edit(embed=embed)
            return

        await self.bot.db.execute('DELETE FROM tags WHERE name = ?', (name,))
        await self.bot.db.commit()

        embed.description = f'Tag `{name}` has been removed.'
        await ctx.edit(embed=embed)

    @tags.command(name='list', description='List all tags.')
    @commands.guild_only()
    async def list_tags(self, ctx: discord.ApplicationContext) -> None:
        await self.bot.db.execute('UPDATE tags SET uses = uses + 1')
        await self.bot.db.commit()

        async with self.bot.db.execute('SELECT * FROM tags') as cursor:
            data = await cursor.fetchall()

        if data is None or len(data) == 0:
            raise commands.BadArgument('There are no tags added.')

        tags = sorted([TagData(*row) for row in data], key=lambda tag: tag.name)
        tag_embeds = list()

        for tag in tags:
            try:
                creator = await self.bot.fetch_user(tag.creator)
                name = f'{creator.name}#{creator.discriminator}'
            except discord.errors.NotFound:
                name = 'Deleted User'

            tag_embeds.append(
                discord.Embed.from_dict(
                    {
                        'title': tag.name,
                        'description': tag.content,
                        'footer': {
                            'text': f"Created by {name} | Used {tag.uses} time{'s' if tag.uses != 1 else ''}",
                            'icon_ url': str(
                                ctx.author.display_avatar.with_static_format('png').url
                            ),
                        },
                    }
                )
            )

        paginator = PaginatorView(tag_embeds, ctx, timeout=180)
        await ctx.respond(
            embed=tag_embeds[paginator.embed_num], view=paginator, ephemeral=True
        )


def setup(bot: discord.Bot):
    bot.add_cog(TagsCog(bot))
