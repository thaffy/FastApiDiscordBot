from typing import Dict, Tuple, List

import httpx
from pydantic import BaseModel, Field

from app.config import settings
from app.utils.logger import logger


class ItemVolumeResponse(BaseModel):
    last_update: int = Field(alias="%LAST_UPDATE%")
    last_update_formatted: str = Field(alias="%LAST_UPDATE_F%")
    items: Dict[str, int] = Field(default_factory=dict)  # Dictionary for dynamic items

    class Config:
        allow_population_by_field_name = True
        extra = "allow"  # Allows additional fields that aren't explicitly defined

    def calculate_volume_scale(self) -> Dict[str, int]:
        volumes = list(self.items.values())
        logger.info(f"Volumes: {len(volumes)}")

        # Get max and min volumes
        max_volume = max(volumes)
        min_volume = min(volumes)

        # Avoid division by zero if max and min volumes are equal
        if max_volume == min_volume:
            return {item: 100 for item in self.items}

        # Scale each volume to a 1-100 range
        return {
            item: int(((volume - min_volume) / (max_volume - min_volume)) * 100)
            for item, volume in self.items.items()
        }

    def get_scaled_sorted_volumes(self) -> List[Tuple[str, int]]:
        # Calculate scaled volumes
        scaled_volumes = self.calculate_volume_scale()

        # Sort items by scaled volume in descending order
        sorted_scaled_volumes = sorted(scaled_volumes.items(), key=lambda x: x[1], reverse=True)

        return sorted_scaled_volumes

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

    async def get_volumes(self) -> ItemVolumeResponse:
        """
        Get trading volumes for items from the OSRS volumes API endpoint.
        Returns an ItemVolumeResponse with logarithmically scaled volumes.
        """
        response = self.client.get(settings.OSRS_VOLUMES_URL)
        data = response.json()

        # Extract the metadata fields
        last_update = data.pop("%LAST_UPDATE%")
        last_update_formatted = data.pop("%LAST_UPDATE_F%")

        # Remove the empty 'items' dictionary if it exists
        data.pop('items', None)

        # Filter out items with 0 volume and sort remaining items
        non_zero_items = {k: v for k, v in data.items() if v > 0}
        sorted_items = sorted(non_zero_items.items(), key=lambda x: x[1], reverse=True)
        zero_items = {k: 0 for k, v in data.items() if v == 0}

        if sorted_items:
            # Use logarithmic scaling for better distribution
            import math

            # Get volume values
            volumes = [v for _, v in sorted_items]

            # Calculate log values (add 1 to handle volumes less than 1)
            log_volumes = [math.log(v + 1) for v in volumes]

            # Get min and max of log values
            min_log = min(log_volumes)
            max_log = max(log_volumes)

            # Calculate scaling factor
            scale_factor = 99 / (max_log - min_log) if max_log != min_log else 1

            # Create scaled dictionary
            scaled_items = {}

            # Scale non-zero items
            for (item_name, volume), log_vol in zip(sorted_items, log_volumes):
                # Scale to 1-100 range
                scaled_value = math.ceil((log_vol - min_log) * scale_factor + 1)
                scaled_items[item_name] = scaled_value

            # Add zero items back
            scaled_items.update(zero_items)
        else:
            scaled_items = data  # If no non-zero items, return original data

        # Create structured data
        structured_data = {
            "%LAST_UPDATE%": last_update,
            "%LAST_UPDATE_F%": last_update_formatted,
            "items": scaled_items
        }

        return ItemVolumeResponse(**structured_data)

    async def get_latest(self) -> LatestItemsResponse:
         return await self._get("/latest")


    async def get_latest_by_item_id(self, item_id: int) -> LatestItemsResponse :
        return await self._get(f"/latest?id={item_id}")

    async def close(self):
        self.client.close()