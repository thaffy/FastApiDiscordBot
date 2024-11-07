from typing import Optional, Dict, List, Tuple

from pydantic import Field, BaseModel


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
    last_update: int = Field(alias="%LAST_UPDATE%")
    last_update_formatted: str = Field(alias="%LAST_UPDATE_F%")
    items: Dict[str, int] = Field(default_factory=dict)  # Dictionary for dynamic items

    class Config:
        allow_population_by_field_name = True
        extra = "allow"  # Allows additional fields that aren't explicitly defined

    def calculate_volume_scale(self) -> Dict[str, int]:
        volumes = list(self.items.values())

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