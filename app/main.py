import asyncio
from contextlib import asynccontextmanager
from datetime import datetime

from discord.errors import HTTPException, LoginFailure

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.dependencies import get_discord_bot, get_gemini_service
from app.routes.discord.router import discord_router
from app.routes.dota.router import dota_router
from app.routes.osrs.router import osrs_router
from app.routes.ssb.router import ssb_router
from app.services.gemini_service import GeminiService
from app.utils.logger import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    start_time = datetime.now()
    discord_bot = await get_discord_bot()
    bot_task = None

    try:
        logger.info("Starting application & Discord bot")
        bot_task = asyncio.create_task(discord_bot.start(settings.DISCORD_TOKEN))
        try:
            await asyncio.sleep(1)

            if bot_task.done() and bot_task.exception():
                raise bot_task.exception()
            logger.info("Application & Discord bot started")
            end_time = datetime.now()
            logger.warn(f"Startup time: {end_time - start_time}")
        except (HTTPException, LoginFailure) as e:
            logger.warning("Discord bot failed to start: Bot features are unavailable")
            logger.warning(f"Error: {e}")
            bot_task = None
        yield

    except Exception as e:
        logger.critical(f"Error in application lifecycle: {e}")

    finally:
        logger.warn("Shutting down application & Discord bot...")

        # Shutdown the bot if it started successfully
        if bot_task and not discord_bot.is_closed():
            await discord_bot.close()

        logger.warn("Application & Discord bot shut down complete")




# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.API_VERSION,
    debug=settings.DEBUG == "debug",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORGINS,
    allow_credentials=settings.ALLOW_CREDENTIALS,
    allow_methods=settings.ALLOW_METHODS,
    allow_headers=settings.ALLOW_HEADERS,
)

app.include_router(dota_router)
app.include_router(ssb_router)
app.include_router(osrs_router)
app.include_router(discord_router)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/llm")
async def llm(llm: GeminiService = Depends(get_gemini_service)):
    return {"response": await llm.generate("Write a short story in 2 sentences")}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app,log_level="critical",access_log=False)