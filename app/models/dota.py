from pydantic import BaseModel
from typing import List, Optional

class Hero(BaseModel):
    id: int
    name: str
    primary_attr: str
    attack_type: str
    roles: List[str]
    img: str
    icon: str
    base_health: int
    base_health_regen: Optional[float] = None
    base_mana: int
    base_mana_regen: float
    base_armor: float
    base_mr: int
    base_attack_min: int
    base_attack_max: int
    base_str: int
    base_agi: int
    base_int: int
    str_gain: float
    agi_gain: float
    int_gain: float
    attack_range: int
    projectile_speed: int
    attack_rate: float
    base_attack_time: int
    attack_point: float
    move_speed: int
    turn_rate: Optional[float] = None
    cm_enabled: bool
    legs: int
    day_vision: int
    night_vision: int
    localized_name: str
