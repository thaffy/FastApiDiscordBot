import google.generativeai as genai
from google.generativeai import GenerativeModel
from setuptools.command.bdist_egg import safety_flags

from app.config import settings


class GeminiService:
    SAFETY_SETTING = [
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_NONE",
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_NONE",
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_NONE",
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_NONE",
        },
    ]


    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)

        self.client: GenerativeModel = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction="You are Lich, the dota2 hero. Your favorite activity is ganking Slark in the jungle, in which you almost always succeed. NEVER incapsulate your entire reponse in quotation marks. NEVER exceed 2000 characters when generating a response."
        )

    async def generate(self, prompt: str):
        response = self.client.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=1000,
                temperature=0.5,
            ),
            safety_settings=self.SAFETY_SETTING,
        )
        return response.text