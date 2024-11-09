from datetime import datetime

from discord.ext import commands

from app.bots.command_handler import CommandHandler
from app.bots.message_handler import setup_message_handler
from app.config import settings
from app.constants import constants
from app.utils.exceptions import DiscordBotNotInitializedError
from app.utils.logger import logger


class DiscordBot:
    _instance: commands.Bot = None

    @classmethod
    async def get_bot(cls) -> commands.Bot:
        if cls._instance is None:
            start_time = datetime.now()
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
                logger.warn(f"Discord Bot Startup time: {datetime.now() - start_time}")

        return cls._instance

    @classmethod
    async def send_system_message(cls, message: str, channel_id: int = constants.OSRS_TRADING_CHANNEL_ID):
        if cls._instance is None:
            raise DiscordBotNotInitializedError

        channel = cls._instance.get_channel(channel_id)
        await channel.send(f"System Message: {message}")
        logger.info(f"Sent system message to channel {channel_id} in guild {channel.guild.name}")
