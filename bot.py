#!/usr/bin/env python3

from dotenv import load_dotenv

import aiohttp
import aiopath
import aiosqlite
import asyncio
import discord
import os
import sys
import time


async def startup():
    if sys.version_info.major < 3 and sys.version_info.minor < 9:
        sys.exit('[ERROR] FDRBot requires Python 3.9 or higher. Exiting.')

    load_dotenv()
    if 'FDRBOT_TOKEN' not in os.environ.keys():
        sys.exit(
            "[ERROR] Bot token not set in 'FDRBOT_TOKEN' environment variable. Exiting."
        )

    if 'FDRBOT_GUILD' not in os.environ.keys():
        sys.exit(
            "[ERROR] Guild ID not set in 'FDRBOT_GUILD' environment variable. Exiting."
        )

    if 'FDRBOT_OWNER' not in os.environ.keys():
        sys.exit(
            "[ERROR] Owner ID(s) not set in 'FDRBOT_OWNER' environment variable. Exiting."
        )

    try:
        debug_guild = [int(os.environ['FDRBOT_GUILD'])]
    except TypeError:
        sys.exit(
            "[ERROR] Invalid guild ID set in 'FDRBOT_GUILD' environment variable. Exiting."
        )

    try:
        owner = int(os.environ['FDRBOT_OWNER'])
    except TypeError:
        sys.exit(
            "[ERROR] Invalid owner ID set in 'FDRBOT_OWNER' environment variable. Exiting."
        )

    mentions = discord.AllowedMentions(everyone=False, roles=False)
    bot = discord.Bot(
        help_command=None,
        intents=discord.Intents.default(),
        allowed_mentions=mentions,
        debug_guilds=debug_guild,
        owner_id=owner,
    )

    bot.load_extension('cogs.utils')  # Load utils cog first
    cogs = aiopath.AsyncPath('cogs')
    async for cog in cogs.glob('*.py'):
        if cog.stem == 'utils':
            continue

        bot.load_extension(f'cogs.{cog.stem}')

    db_path = aiopath.AsyncPath('Data/FDRBot.db')
    await db_path.parent.mkdir(exist_ok=True)
    async with aiosqlite.connect(db_path) as db, aiohttp.ClientSession() as session:
        await db.execute(
            '''
            CREATE TABLE IF NOT EXISTS tags(
            name STRING,
            content STRING,
            uses INTEGER,
            creator INTEGER
            )
            '''
        )
        await db.commit()

        await db.execute(
            '''
            CREATE TABLE IF NOT EXISTS uptime(
            start_time REAL
            )'''
        )
        await db.commit()

        async with db.execute('SELECT start_time FROM uptime') as cursor:
            if await cursor.fetchone() is None:
                sql = 'INSERT INTO uptime(start_time) VALUES(?)'
            else:
                sql = 'UPDATE uptime SET start_time = ?'

        await db.execute(sql, (await asyncio.to_thread(time.time),))
        await db.commit()

        # Setup bot attributes
        bot.db = db
        bot.session = session

        try:
            await bot.start(os.environ['FDRBOT_TOKEN'])
        except discord.LoginFailure:
            sys.exit(
                "[ERROR] Token invalid, make sure the 'FDRBOT_TOKEN' environment variable is set to your bot token. Exiting."
            )
        finally:
            await bot.close()


if __name__ == '__main__':
    try:
        asyncio.run(startup())
    except KeyboardInterrupt:
        pass
