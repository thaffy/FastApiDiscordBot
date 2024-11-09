import json
import os
from typing import Optional, Dict

from app.models.dota import Hero
from app.models.runescape import OsrsItem
from app.utils.logger import logger




class Constants:

    ## Player Ids
    THAFFY_DOTA_ID: int = 62590060
    LARIUS_DOTA_ID: int = 31679778
    KYO0X_DOTA_ID: int = 2592025
    ADAM_DOTA_ID: int = 76630363

    ## Dota 2 stuff
    DOTA_RANKS = [
        (1, 12, "Herald"),
        (13, 25, "Guardian"),
        (26, 37, "Crusader"),
        (38, 50, "Archon"),
        (51, 62, "Legend"),
        (63, 75, "Ancient"),
        (76, 88, "Divine"),
        (89, 100, "Immortal")
    ]

    # Discord Channel Ids
    OSRS_TRADING_CHANNEL_ID: int = 1303857091643052124

    ## Discord Bot Predefined reponses
    PREDEFINED_RESPONSES = [
        {
            "triggers": ["we'll see", "we will see"],
            "response": "already reported"
        },
        {
            "triggers": ["i got a bone to pick"],
            "response": "I don't want you monkey mouth motherfuckers sitting in my throne again"
        },
        {
            "triggers": ["polak"],
            "response": "https://tenor.com/view/proboscis-monkey-eating-chewing-hungry-curious-gif-9771337"
        },
        {
            "triggers": ["hey you"],
            "response": "you're finally woke"
        },
        {
            "triggers": ["shapiro","trump","adolf","hitler","peterson","tate"],
            "response": "chuds please help me"
        },
        {
            "triggers": ["sup"],
            "response": "https://i.ibb.co/vB7S4zM/Screenshot-2024-10-26-220718.png"
        },
        {
            "triggers": ["nice"],
            "response": "https://i.ibb.co/MDgx8kN/thaffster.png"
        },
        {
            "triggers": ["build","built"],
            "response": "YOU BUILDA SHIET!!!!!!"
        }
    ]

    OSRSITEMLIST: Dict[int,OsrsItem] = {}
    DOTAHEROESLIST: Dict[int,Hero] = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_player_ids(self):
        return [self.THAFFY_DOTA_ID, self.LARIUS_DOTA_ID, self.KYO0X_DOTA_ID, self.ADAM_DOTA_ID]

    def get_dota_rank_by_tier(self, tier: int) -> str:
        if tier is None:
            return "Uncalibrated"
        if tier < 1 or tier > 100:
            return "Unknown"

        for start, end, rank_name in self.DOTA_RANKS:
            if start <= tier <= end:
                return rank_name

    def get_predefined_response(self, message_content: str) -> Optional[str]:
        message_content_lower = message_content.lower()
        for item in self.PREDEFINED_RESPONSES:
            if any(trigger in message_content_lower for trigger in item["triggers"]):
                return item["response"]
        return None

    def load_osrs_item_map(self):
        try:
            file_path = os.path.join(os.path.dirname(__file__), "json_files/osrs_item_map.json")
            with open(file_path, "r") as file:
                items = [OsrsItem(**item) for item in json.load(file)]
            self.OSRSITEMLIST = {item.id: item for item in items}
        except FileNotFoundError:
            logger.error("The osrs_item_map.json file was not found.")
            return []
        except json.JSONDecodeError:
            logger.error("Error decoding JSON in osrs_item_map.json.")
            return []

    def load_dota_heroes_map(self):
        try:
            file_path = os.path.join(os.path.dirname(__file__), "json_files/heroes.json")
            with open(file_path, "r") as file:
                data = json.load(file)
                items = [Hero(**hero_data) for hero_data in data.values()]
            self.DOTAHEROESLIST = {item.id: item for item in items}
        except FileNotFoundError:
            logger.error("The osrs_item_map.json file was not found.")
            return []
        except json.JSONDecodeError:
            logger.error("Error decoding JSON in osrs_item_map.json.")
            return []




constants = Constants()
constants.load_osrs_item_map()
constants.load_dota_heroes_map()
logger.info(f"Constants Setup Complete!")
