import discord


class EventsCog(discord.Cog, name='Events'):
    def __init__(self, bot):
        self.bot = bot

    @discord.Cog.listener()
    async def on_ready(self) -> None:
        print('FDRBot is now online.')


def setup(bot: discord.Bot):
    bot.add_cog(EventsCog(bot))
