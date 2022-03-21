#!/usr/bin/env python3

from dotenv.main import load_dotenv

import aiohttp
import aiopath
import aiosqlite
import asyncio
import discord
import os
import sys
import time


DB_PATH = aiopath.AsyncPath('Data/FDRBot.db')


async def main():
    if sys.version_info[:2] < (3, 9):
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

    await DB_PATH.parent.mkdir(exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db, aiohttp.ClientSession() as session:
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
            CREATE TABLE IF NOT EXISTS logs(
            guild INTEGER,
            channel INTEGER
            )
            '''
        )
        await db.commit()

        # Setup bot attributes
        bot.db = db
        bot.session = session
        bot.start_time = await asyncio.to_thread(time.time)

        try:
            await bot.start(os.environ['FDRBOT_TOKEN'])
        except discord.LoginFailure:
            sys.exit(
                "[ERROR] Token invalid, make sure the 'FDRBOT_TOKEN' environment variable is set to your bot token. Exiting."
            )


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
