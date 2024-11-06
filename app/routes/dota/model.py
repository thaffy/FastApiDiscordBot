from typing import Optional

from pydantic import BaseModel

class ProPlayer(BaseModel):
    account_id: Optional[int]
    steamid: Optional[str]
    avatar: Optional[str]
    avatarmedium: Optional[str]
    avatarfull: Optional[str]
    profileurl: Optional[str]
    personaname: Optional[str]
    last_login: Optional[str]
    full_history_time: Optional[str]
    cheese: Optional[int]
    fh_unavailable: Optional[bool]
    loccountrycode: Optional[str]
    name: Optional[str]
    country_code: Optional[str]
    fantasy_role: Optional[int]
    team_id: Optional[int]
    team_name: Optional[str]
    team_tag: Optional[str]
    is_locked: Optional[bool]
    is_pro: Optional[bool]
    locked_until: Optional[int]


class ProPlayerProfile(BaseModel):
    account_id: Optional[int]
    personaname: Optional[str]
    team_name: Optional[str]
    steamid: Optional[str]
    profileurl: Optional[str]
    avatar: Optional[str]
    avatarmedium: Optional[str]
    avatarfull: Optional[str]
