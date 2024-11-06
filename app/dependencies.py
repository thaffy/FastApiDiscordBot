from discord.ext import commands

from app.config import settings
from app.services.dota_service import DotaService
from app.services.gemini_service import GeminiService
from app.services.ssb_service import SsbService
from app.bots.discord_bot import DiscordBot


###
# This file is used to create a dependency injection container
# This is a way to manage the creation of services and other dependencies
###

def get_ssb_service() -> SsbService:
    return SsbService(base_url=settings.SSB_BASE_URL)

def get_dota_service() -> DotaService:
    return DotaService(base_url=settings.OPENDOTA_BASE_URL)

async def get_discord_bot() -> commands.Bot:
    return await DiscordBot.get_bot()

def get_gemini_service() -> GeminiService:
    return GeminiService()