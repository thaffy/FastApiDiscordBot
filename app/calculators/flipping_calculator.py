import math
from typing import Dict

import numpy as np
from pydantic import BaseModel

from app.models.runescape import OsrsItem, LatestItemsResponse, FlippingResult, ItemVolumeResponse
from app.utils.logger import logger


class FlippingCalculator:
    TAX_RATE = 0.01
    ITEM_VOLUMES : ItemVolumeResponse = None
    VOLUME_PERCENTILES = [0, 0, 0, 0, 0]

    def __init__(self):
        self.cache: Dict[int, FlippingResult] = {}
        logger.info("FlippingCalculator initialized")

    def invalidate_cache(self):
        self.cache = {}

    def invalidate_item_cache(self, item_id: int):
        self.cache.pop(item_id, None)

    def set_item_volumes (self, item_volumes: ItemVolumeResponse):
        self.ITEM_VOLUMES = item_volumes
        volume_values = [volume for _, volume in item_volumes.items.values()]
        self.VOLUME_PERCENTILES = np.percentile(volume_values, [25, 50, 75, 90, 95])

    def score_volume(self, volume: int) -> float:
        """
        Score the trade volume on a scale of 0-1.
        Uses percentile-based scoring for better distribution.
        """
        if volume >= self.VOLUME_PERCENTILES[4]:  # 95th percentile
            return 1.0
        elif volume >= self.VOLUME_PERCENTILES[3]:  # 90th percentile
            return 0.9
        elif volume >= self.VOLUME_PERCENTILES[2]:  # 75th percentile
            return 0.75
        elif volume >= self.VOLUME_PERCENTILES[1]:  # 50th percentile
            return 0.5
        elif volume >= self.VOLUME_PERCENTILES[0]:  # 25th percentile
            return 0.25
        else:
            return 0.1

    def calculate(self, item: OsrsItem, price: LatestItemsResponse) -> FlippingResult:

        high_price = price["data"][str(item.id)]["high"]
        low_price = price["data"][str(item.id)]["low"]
        diff = high_price - low_price

        cash_needed = low_price * item.limit
        tax_rate = self.TAX_RATE if high_price > 100 else 0

        profit = ((high_price * (1 - tax_rate)) - low_price) * item.limit
        profit_no_tax = (high_price - low_price) * item.limit
        profit_per_item = (high_price * (1 -tax_rate)) - low_price
        profit_per_item_no_tax = high_price - low_price

        total_cost = low_price * item.limit
        roi = (profit / total_cost) * 100 if total_cost > 0 else 0
        roi_per_item = (profit_per_item / low_price) * 100

        flipping_result = FlippingResult(
            item_name="Not given",
            high_price=high_price,
            low_price=low_price,
            price_diff=math.floor(diff),
            cash_needed=math.ceil(cash_needed),
            total_profit=math.floor(profit),
            profit_no_tax=math.floor(profit_no_tax),
            profit_per_item=math.floor(profit_per_item),
            profit_per_item_no_tax=math.floor(profit_per_item_no_tax),
            total_cost=math.ceil(total_cost),
            roi_percentage=roi,
            roi_per_item=roi_per_item,
            limit=item.limit,
            score= 0
        )

        return flipping_result

    def calculate_v2(self, limit: int, high_price: int, low_price: int,item_name: str) -> FlippingResult:

        diff = high_price - low_price

        cash_needed = low_price * limit
        tax_rate = self.TAX_RATE if high_price > 100 else 0

        profit = ((high_price * (1 - tax_rate)) - low_price) * limit
        profit_no_tax = (high_price - low_price) * limit
        profit_per_item = (high_price * (1 -tax_rate)) - low_price
        profit_per_item_no_tax = high_price - low_price

        total_cost = low_price * limit
        roi = (profit / total_cost) * 100 if total_cost > 0 else 0
        roi_per_item = (profit_per_item / low_price) * 100

        flipping_result = FlippingResult(
            item_name=item_name,
            high_price=high_price,
            low_price=low_price,
            price_diff=diff,
            cash_needed=math.ceil(cash_needed),
            total_profit=math.floor(profit),
            profit_no_tax=math.floor(profit_no_tax),
            profit_per_item=math.floor(profit_per_item),
            profit_per_item_no_tax=math.floor(profit_per_item_no_tax),
            total_cost=math.ceil(total_cost),
            roi_percentage=math.floor(roi),
            roi_per_item=math.floor(roi_per_item),
            limit=limit,
            score = 0
        )

        return flipping_result

    def calculate_v3(self,limit: int, high_price: int, low_price: int,item_name: str):
        pass
