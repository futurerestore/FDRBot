from discord.ext import commands
from typing import Union
import aiosqlite
import remotezip


class Utils(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_manifest(self, url: str, dir: str) -> Union[bool, str]:
        try:
            with remotezip.RemoteZip(url) as ipsw:
                return ipsw.read(next(f for f in ipsw.namelist() if 'BuildManifest' in f))
        except remotezip.RemoteIOError:
            return False

    async def get_prefix(self, guild: int) -> str:
        async with aiosqlite.connect('Data/fdrbot.db') as db, db.execute('SELECT prefix FROM prefix WHERE guild = ?', (guild,)) as cursor:
            try:
                guild_prefix = (await cursor.fetchone())[0]
            except TypeError:
                await db.execute('INSERT INTO prefix(guild, prefix) VALUES(?,?)', (guild, 'b!'))
                await db.commit()
                guild_prefix = 'b!'

        return guild_prefix

def setup(bot):
    bot.add_cog(Utils(bot))
