from typing import Optional,Dict, List, Tuple
import numpy as np
from pydantic import Field, BaseModel, RootModel


class FlippingResult(BaseModel):
    item_name: Optional[str]
    high_price: int
    low_price: int
    price_diff: int
    cash_needed: int
    total_profit: int
    profit_no_tax: int
    profit_per_item: int
    profit_per_item_no_tax: int
    total_cost: int
    roi_percentage: float
    roi_per_item: float
    limit: int
    score: int

class DiscordFlippingResult(BaseModel):
    item_name: Optional[str]
    high_price: int
    low_price: int
    total_profit: int
    roi_percentage: float
    cash_needed: int


class OsrsItem(BaseModel):
    examine: Optional[str]
    id: int
    members: Optional[bool]
    lowalch: Optional[int] = 0
    limit: Optional[int] = 100000
    value: Optional[int]
    highalch: Optional[int] = 0
    icon: Optional[str]
    name: Optional[str]





class ItemVolumeResponse(BaseModel):
    timestamp: int = Field(alias="%LAST_UPDATE%")
    timestamp_formatted: str = Field(alias="%LAST_UPDATE_F%")
    volumes: Dict[str, int] = {}

    class Config:
        populate_by_name = True

    def __init__(self, **data):
        # Extract timestamp fields
        timestamp = data.pop("%LAST_UPDATE%", 0)
        timestamp_formatted = data.pop("%LAST_UPDATE_F%", "")
        # Remaining data becomes volumes
        super().__init__(
            timestamp=timestamp,
            timestamp_formatted=timestamp_formatted,
            volumes=data
        )

    def get_volume(self, item_name: str) -> int:
        """Get volume for a specific item."""
        return self.volumes.get(item_name, 0)

    def get_scaled_volumes(self) -> Dict[str, int]:
        """Scale volumes to 1-100 range."""
        volumes = list(self.volumes.values())
        if not volumes:
            return {}

        max_vol = max(volumes)
        min_vol = min(volumes)

        if max_vol == min_vol:
            return {item: 100 for item in self.volumes}

        return {
            item: int(((vol - min_vol) / (max_vol - min_vol)) * 100)
            for item, vol in self.volumes.items()
        }

    def get_sorted_volumes(self, scaled: bool = False) -> List[Tuple[str, int]]:
        """Get volumes sorted by value, optionally scaled."""
        data = self.get_scaled_volumes() if scaled else self.volumes
        return sorted(data.items(), key=lambda x: x[1], reverse=True)

    def get_percentiles(self) -> np.ndarray:
        """Calculate volume percentiles."""
        volumes = list(self.volumes.values())
        return np.percentile(volumes, [25, 50, 75, 90, 95])

class LatestItemEntry(BaseModel):
    high: int
    highTime: int
    low: int
    lowTime: int

class LatestItemsResponse(BaseModel):
    data: Dict[str, LatestItemEntry]