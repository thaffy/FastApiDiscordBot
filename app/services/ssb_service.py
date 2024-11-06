import httpx
import pandas as pd


class SsbService:
    def __init__(self,base_url: str):
        self.base_url = base_url
        self.client = httpx.Client()

        if self.base_url is None:
           raise Exception("base_url is required to use SsbService")

    async def _get(self, endpoint: str):
            response = self.client.get(f"{self.base_url}{endpoint}")
            return response.json()

    async def get_tables(self):
        return await self._get(f"/table")

    async def get_unemployment(self):
        data = await self._get(f"/table/13760")
        dataframe = pd.DataFrame(data)
        head = dataframe.head()
        print(head)

        return dataframe
