import math
from typing import Dict

from pydantic import BaseModel

from app.constants import OsrsItem
from app.services.osrs_service import LatestItemsResponse


class FlippingResult(BaseModel):
    high_price: int
    low_price: int
    price_diff: int
    cash_needed: int
    total_profit: int
    profit_no_tax: int
    profit_per_item: int
    total_cost: int
    roi_percentage: float
    roi_per_item: float
    limit: int

class FlippingCalculator:
    TAX_RATE = 0.01

    def __init__(self):
        self.cache: Dict[int, FlippingResult] = {}

    def invalidate_cache(self):
        self.cache = {}

    def invalidate_item_cache(self, item_id: int):
        self.cache.pop(item_id, None)

    def calculate(self, item: OsrsItem, price: LatestItemsResponse) -> FlippingResult:

        high_price = price["data"][str(item.id)]["high"]
        low_price = price["data"][str(item.id)]["low"]
        diff = high_price - low_price

        cash_needed = low_price * item.limit

        profit = ((high_price * (1 - self.TAX_RATE)) - low_price) * item.limit
        profit_no_tax = (high_price - low_price) * item.limit
        profit_per_item = (high_price * (1 - self.TAX_RATE)) - low_price

        total_cost = low_price * item.limit
        roi = (profit / total_cost) * 100 if total_cost > 0 else 0
        roi_per_item = (profit_per_item / low_price) * 100

        flipping_result = FlippingResult(
            high_price=high_price,
            low_price=low_price,
            price_diff=math.floor(diff),
            cash_needed=math.ceil(cash_needed),
            total_profit=math.floor(profit),
            profit_no_tax=math.floor(profit_no_tax),
            profit_per_item=math.floor(profit_per_item),
            total_cost=math.ceil(total_cost),
            roi_percentage=roi,
            roi_per_item=roi_per_item,
            limit=item.limit
        )

        return flipping_result

    # def bulk_calculate() -> Dict[int, FlippingResult]:
    #     return {item_id: self.calculate(item, price) for item_id, item in items.items()}
