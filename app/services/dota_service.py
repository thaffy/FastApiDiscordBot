import httpx


class DotaService:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.Client()

        if self.base_url is None or self.base_url == "":
           raise Exception("base_url is required to use DotaService")

    async def _get(self, endpoint: str):
        response = self.client.get(f"{self.base_url}{endpoint}")
        return response.json()

    async def health(self):
        return await self._get("/health")


    async def get_pro_players(self):
        return await self._get(f"/proPlayers")

    async def get_player(self, id: int):
        return await self._get(f"/players/{id}")

    async def get_match(self, match_id: int):
        return await self._get(f"/matches/{match_id}")

