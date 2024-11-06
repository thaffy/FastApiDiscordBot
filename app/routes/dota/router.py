from typing import List, Optional
from fastapi import APIRouter
from fastapi.params import Depends

from app.dependencies import get_dota_service
from app.routes.dota.model import ProPlayerProfile
from app.services.dota_service import DotaService

dota_router = APIRouter(prefix="/dota", tags=["dota"])

@dota_router.get("/pros",response_model=List[ProPlayerProfile])
async def get_pros(dota_service: DotaService = Depends(get_dota_service)):
    return await dota_service.get_pro_players()

@dota_router.get("/player/{player_id}")
async def get_player(player_id: int, dota_service: DotaService = Depends(get_dota_service)):
    return await dota_service.get_player(player_id)


