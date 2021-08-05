# FDRBot

[![License](https://img.shields.io/github/license/m1stadev/FDRBot)](https://github.com/m1stadev/FDRBot)
[![Stars](https://img.shields.io/github/stars/m1stadev/FDRBot)]((https://github.com/m1stadev/FDRBot))
[![LoC](https://img.shields.io/tokei/lines/github/m1stadev/FDRBot)](https://github.com/m1stadev/FDRBot)

FDRBot is a moderation bot for the [FutureRestore](https://github.com/m1stadev/futurerestore) support server

## Running

To locally host your own instance, [create a Discord bot](https://discord.com/developers) and follow these steps:

1. Create a virtual env and install dependencies

        python3 -m venv --upgrade-deps env; source env/bin/activate
        pip3 install -U -r requirements.txt

2.  Set the `FDRBOT_TOKEN` environment variable to the bot token you got from your Discord bot application

    This can be done by exporting `FDRBOT_TOKEN` in should shell configuration file, then reloading your shell

3. Start your instance

        python3 bot.py

## Support

For any questions/issues you have, join my [Discord](https://m1sta.xyz/discord).
