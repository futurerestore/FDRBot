#!/usr/bin/env python3

from discord.ext import commands
import aiosqlite
import discord
import glob
import os
import platform
import sys


def bot_token():
    if os.getenv('FDRBOT_TOKEN') is not None:
        return os.getenv('FDRBOT_TOKEN')
    else:
        sys.exit("[ERROR] Bot token not set in 'FDRBOT_TOKEN' environment variable. Exiting.")

async def get_prefix(client, message):
    if message.channel.type is discord.ChannelType.private:
        return 'b!'

    async with aiosqlite.connect('Data/fdrbot.db') as db, db.execute('SELECT prefix FROM prefix WHERE guild = ?', (message.guild.id,)) as cursor:
        try:
            guild_prefix = (await cursor.fetchone())[0]
        except TypeError:
            await db.execute('INSERT INTO prefix(guild, prefix) VALUES(?,?)', (message.guild.id, '!'))
            await db.commit()
            guild_prefix = '!'

    return commands.when_mentioned_or(guild_prefix)(client, message)

def main():
    if platform.system() == 'Windows':
        sys.exit('[ERROR] FDRBot is not supported on Windows. Exiting.')

    mentions = discord.AllowedMentions(everyone=False, roles=False)
    
    client = commands.AutoShardedBot(
        help_command=None,
        command_prefix=get_prefix,
        allowed_mentions=mentions
    )

    client.load_extension('cogs.utils') # Load utils cog first

    for cog in glob.glob('cogs/*.py'):
        if 'utils.py' in cog:
            continue

        client.load_extension(cog.replace('/', '.')[:-3])

    try:
        client.run(bot_token())
    except discord.LoginFailure:
        sys.exit("[ERROR] Token invalid, make sure the 'FDRBOT_TOKEN' environment variable is set to your bot token. Exiting.")

if __name__ == '__main__':
    main()
