import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.dependencies import get_discord_bot, get_gemini_service
from app.routes.dota.router import dota_router
from app.routes.osrs.router import osrs_router
from app.routes.ssb.router import ssb_router
from app.services.gemini_service import GeminiService
from app.utils.logger import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    discord_bot = await get_discord_bot()
    try:
        logger.info("Starting application & Discord bot")

        ## Start Discord Bot
        asyncio.create_task(discord_bot.start(settings.DISCORD_TOKEN))

        logger.info("Application & Discord bot started")
        yield
    except Exception as e:
        logger.error(f"Error in application lifecycle: {e}")
    finally:
        logger.info("Shutting down application & Discord bot")
        if not discord_bot.is_closed():
            await discord_bot.close()

        logger.info("Application & Discord bot shut down")

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