from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_discord_service
from app.utils.exceptions import DiscordBotNotInitializedError

discord_router = APIRouter(prefix="/discord", tags=["discord"])


@discord_router.get("/system_message")
async def send_system_message(message: str, discord_bot = Depends(get_discord_service)):
    try:

        await discord_bot.send_system_message(message)
        return HTTPStatus.OK
    except DiscordBotNotInitializedError as e:
        raise HTTPException(status_code=HTTPStatus.SERVICE_UNAVAILABLE, detail=str(e))
