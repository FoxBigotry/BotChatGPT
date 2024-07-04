import httpx
import logging
from ai.context import load_system_prompt,build_context
from settings import settings
from openai import AsyncOpenAI
from database.connect import MongoDBActions


mongo_actions = MongoDBActions()


class OpenAi_default:
    def __init__(self, default_model: str = settings.DEFAULT_MODEL, prompt_path: str = 'ai/default/uni_agent.md'):
        if settings.PROXY:
            self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY,
                                      http_client=httpx.AsyncClient(
                                          proxies=settings.PROXY,
                                          transport=httpx.HTTPTransport(local_address="0.0.0.0")
                                      ))
        else:
            self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

        self.agent_system_prompt = load_system_prompt(prompt_path)
        self.default_model = default_model

    async def gpt4(self, question, user_id, chat_topic, prompt_path: str = 'ai/default/uni_agent.md'):
        context = await build_context(user_id, chat_topic, question, prompt_path)
        try:
            response = await self.client.chat.completions.create(
                messages=context,
                model=settings.DEFAULT_MODEL,
                temperature=settings.DEFAULT_TEMPERATURE,
            )
            return response.choices[0].message.content
        except Exception as e:
            logging.error(f"Error during OpenAI request: {e}")
            print(f"error: {str(e)}")
