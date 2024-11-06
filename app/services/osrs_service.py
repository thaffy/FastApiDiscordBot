from typing import Dict

import httpx
from pydantic import BaseModel

from app.config import settings


class LatestItemEntry(BaseModel):
    high: int
    highTime: int
    low: int
    lowTime: int

class LatestItemsResponse(BaseModel):
    data: Dict[str, LatestItemEntry]



class OsrsService:
    def __init__(self,base_url: str):
        self.client = httpx.Client()
        self.client.headers.update({"User-Agent": "Discord Bot: @Thaffy on Discord"})
        self.base_url = base_url

        if self.base_url is None:
            raise Exception("base_url is required to use OsrsService")

    async def _get(self, endpoint: str):
        result = self.client.get(f"{self.base_url}{endpoint}")
        return result.json()

    async def get_volumes(self):
        result = self.client.get(settings.OSRS_VOLUMES_URL)
        return result.json()

    async def get_latest(self) -> LatestItemsResponse:
         return await self._get("/latest")

    async def get_latest_by_item_id(self, item_id: int) -> LatestItemsResponse :
        return await self._get(f"/latest?id={item_id}")