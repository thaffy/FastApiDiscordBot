from typing import Optional

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
        }
    ]

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

    def _create_response_map(self):
        response_map = {}
        for item in self.PREDEFINED_RESPONSES:
            for trigger in item["triggers"]:
                response_map[trigger.lower()] = item["response"]
        return response_map

    def get_predefined_response(self, message_content: str) -> Optional[str]:
        message_content_lower = message_content.lower()
        for item in self.PREDEFINED_RESPONSES:
            if any(trigger in message_content_lower for trigger in item["triggers"]):
                return item["response"]
        return None


constants = Constants()
