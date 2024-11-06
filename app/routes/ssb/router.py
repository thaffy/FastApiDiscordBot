from fastapi import APIRouter
from fastapi.params import Depends

from app.dependencies import get_ssb_service
from app.services.ssb_service import SsbService

ssb_router = APIRouter(prefix="/ssb", tags=["ssb"])

@ssb_router.get("/tables")
async def get_tables(ssb_service: SsbService = Depends(get_ssb_service)):
    return await ssb_service.get_tables()

@ssb_router.get("/tables/unemployment")
async def get_unemployment(ssb_service: SsbService = Depends(get_ssb_service)):
    return await ssb_service.get_unemployment()