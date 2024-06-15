import httpx
import logging
from ai.context import create_chat_context
from settings import settings
from openai import AsyncOpenAI
from database.connect import MongoDBActions


mongo_actions = MongoDBActions()


class OpenAi:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY,
                                  http_client=httpx.AsyncClient(
                                      proxies=settings.PROXY,
                                      transport=httpx.HTTPTransport(local_address="0.0.0.0")
                                  ))

    async def gpt4(self, question, user_id):
        last_text = await mongo_actions.get_user_messages(user_id)
        context = await create_chat_context(last_text)
        context.append({"role": "user", "content": str(question)})
        try:
            response = await self.client.chat.completions.create(
                messages=context,
                model="gpt-4o-2024-05-13"
            )
            return response
        except Exception as e:
            logging.error(f"Error during OpenAI request: {e}")
            print(f"error: {str(e)}")
