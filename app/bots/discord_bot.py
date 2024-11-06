
from typing import Optional

from discord.ext import commands

from app.bots.command_handler import CommandHandler
from app.bots.message_handler import setup_message_handler
from app.config import settings
from app.utils.logger import logger


class DiscordBot:
    _instance: commands.Bot = None

    @classmethod
    async def get_bot(cls) -> commands.Bot:
        if cls._instance is None:
            intents = settings.DISCORD_INTENTS
            intents.members = True
            intents.message_content = True

            cls._instance = commands.Bot(
                command_prefix=settings.DISCORD_COMMAND_PREFIX,
                intents=intents
            )

            ## Handlers for message events and command invocation
            setup_message_handler(cls._instance)
            await cls._instance.add_cog(CommandHandler(cls._instance))

            ## Logger events
            @cls._instance.event
            async def on_connect():
                logger.info(f"Connected to Discord with appid {cls._instance.application.id}")


            @cls._instance.event
            async def on_ready():
                logger.info(f"Logged in as {cls._instance.user}")
                logger.info(f'Bot is in {len(cls._instance.guilds)} guilds')

        return cls._instance
