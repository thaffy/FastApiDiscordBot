from fastapi import APIRouter, Depends

from app.dependencies import get_osrs_service
from app.services.osrs_service import OsrsService

osrs_router = APIRouter(prefix="/osrs", tags=["osrs"])

@osrs_router.get("/items")
async def get_items(osrs_service: OsrsService = Depends(get_osrs_service)):
    return await osrs_service.get_latest()

@osrs_router.get("/items/volumes")
async def get_item_volumes(osrs_service: OsrsService = Depends(get_osrs_service)):
    return await osrs_service.get_volumes()


@osrs_router.get("/items/{item_id}")
async def get_item(item_id: int, osrs_service: OsrsService = Depends(get_osrs_service)):
    return await osrs_service.get_latest_by_item_id(item_id)