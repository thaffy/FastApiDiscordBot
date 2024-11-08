from typing import Optional

import httpx
from app.config import settings
from app.constants import constants
from app.models.runescape import ItemVolumeResponse, LatestItemsResponse, OsrsItem
from app.utils.logger import logger

class OsrsService:

    OSRS_ITEM_MAPPINGS = constants.OSRSITEMLIST

    def __init__(self,base_url: str):
        self.client = httpx.Client()
        self.client.headers.update({"User-Agent": "Discord Bot: @Thaffy on Discord"})
        self.base_url = base_url

        if self.base_url is None:
            raise Exception("base_url is required to use OsrsService")

        if constants.OSRSITEMLIST.items() is None:
            try:
                self.OSRS_ITEM_MAPPINGS = constants.load_osrs_item_map()
            except Exception as e:
                logger.error(f"Error loading osrs item map: {e}")

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

        return data

    async def get_volumes_scaled(self) -> ItemVolumeResponse:
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

    def get_osrs_item_by_id(self, item_id: int) -> Optional[OsrsItem]:
        return self.OSRS_ITEM_MAPPINGS.get(item_id)

    def get_osrs_item_by_name(self, name: str) -> Optional[OsrsItem]:
        for item in self.OSRS_ITEM_MAPPINGS.values():
            if item.name.lower() == name.lower():
                return item
        return None

    async def close(self):
        self.client.close()