from datetime import datetime
from typing import Optional

from discord import Message

from app.config import settings
from app.constants import constants
from app.utils.logger import logger


class MessageHandler:
    def __init__(self, bot):
        from app.dependencies import get_gemini_service
        self.bot = bot
        self.llm_last_message_sent = None
        self.llm_channel = "deltabotshome" ## Only works in DeltaSplit's server
        self.llm_service = get_gemini_service()

    async def handle_message(self, message: Message) -> None:
        """Main message handling logic."""
        if self._should_ignore_message(message):
            return

        self._log_message(message)

        if await self._handle_command(message):
            return

        if await self._handle_predefined_response(message):
            return

        await self._handle_llm_response(message)

    ## Utility class methods beyond this point ##
    def _should_ignore_message(self, message: Message) -> bool:
        """Check if message should be ignored."""
        return message.author == self.bot.user or message.content is None

    def _log_message(self, message: Message) -> None:
        """Log the incoming message."""
        logger.info(
            f"{message.guild.name}/#{message.channel.name.lower()}: "
            f"{message.author}: {message.content}"
        )

    async def _handle_command(self, message: Message) -> bool:
        """Handle bot commands."""
        if message.content.strip().startswith(settings.DISCORD_COMMAND_PREFIX):
            await self.bot.process_commands(message)
            return True
        return False

    async def _handle_predefined_response(self, message: Message) -> bool:
        """Handle predefined responses."""
        if response := constants.get_predefined_response(message.content):
            await message.channel.send(response)
            return True
        return False

    async def _handle_llm_response(self, message: Message) -> None:
        """Handle LLM-generated responses."""
        if message.channel.name.lower() != self.llm_channel:
            return

        if self._is_llm_on_cooldown():
            logger.info("LLM is on cooldown...")
            return

        prompt = self._get_llm_prompt(message.content)
        response = await self._generate_llm_response(prompt, message.content)

        if response and self._is_valid_response(response):
            await message.channel.send(response)
            self.llm_last_message_sent = datetime.now()

    def _is_llm_on_cooldown(self) -> bool:
        """Check if LLM is on cooldown."""
        if not self.llm_last_message_sent:
            return False

        cooldown_elapsed = datetime.now() - self.llm_last_message_sent
        return cooldown_elapsed < settings.LLM_COOLDOWN_DURATION

    def _get_llm_prompt(self, content: str) -> str:
        """Get appropriate prompt based on message content."""
        return (
            "Write a summarized, intelligent answer to this question "
            "(FEWER THAN 2000 CHARACTERS IN LENGTH!)"
            if content.strip().endswith('?')
            else "Reply in 1-3 sentences to the following text:"
        )

    async def _generate_llm_response(self, prompt: str, content: str) -> Optional[str]:
        """Generate response using LLM service."""
        try:
            return await self.llm_service.generate(f"{prompt}: {content}")
        except Exception as e:
            logger.error(f"Error generating LLM response: {e}")
            return None

    def _is_valid_response(self, response: str) -> bool:
        """Check if the response is valid and not a default error message."""
        return response != (
            "Please provide me with the question you'd like me to answer. "
            "I need the question to understand what you're asking and "
            "provide a summarized, intelligent response."
        )

def setup_message_handler(bot):
    handler = MessageHandler(bot)

    @bot.event
    async def on_message(message: Message):
        await handler.handle_message(message)