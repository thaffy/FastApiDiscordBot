from datetime import timedelta
from typing import List

import discord
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.utils.logger import logger


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env",env_file_encoding="utf-8")

    # FastAPI Settings
    APP_NAME: str = "Dota 2 API"
    API_VERSION: str = "v1"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    ## FastAPI CORS Settings
    CORS_ORGINS: List[str] = ["*"]
    ALLOW_CREDENTIALS: bool = True
    ALLOW_METHODS: List[str] = ["*"]
    ALLOW_HEADERS: List[str] = ["*"]

    ## Base Urls:
    SSB_BASE_URL: str = 'https://api.opendota.com/api'
    OPENDOTA_BASE_URL: str = 'https://data.ssb.no/api/v0/no'
    OSRS_BASE_URL: str = 'https://prices.runescape.wiki/api/v1/osrs'

    ## Other URLs
    OSRS_VOLUMES_URL: str = 'https://oldschool.runescape.wiki/?title=Module:GEVolumes/data.json&action=raw&ctype=application%2Fjson'

    ## Redis Settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    ## Database Settings
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = ""
    DB_PASSWORD: str = ""
    DB_NAME: str = ""

    ## Discord Bot
    DISCORD_TOKEN: str = "" # Set in .env
    DISCORD_COMMAND_PREFIX: str = "$"
    DISCORD_INTENTS: discord.Intents = discord.Intents.default()

    ## LLMS
    GEMINI_API_KEY: str = "" # Set in .env
    LLM_COOLDOWN_DURATION : timedelta = timedelta(seconds=1)  # set to your desired duration

    def __init__(self,**kwargs):
        super().__init__(**kwargs)

settings = Settings()
logger.info(f"Settings Setup Complete!")