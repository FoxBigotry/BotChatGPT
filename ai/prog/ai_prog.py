import httpx
import logging
from ai.context import load_system_prompt, build_context
from settings import settings
from openai import AsyncOpenAI


class OpenAi_prog:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY,
                                  http_client=httpx.AsyncClient(
                                      proxies=settings.PROXY,
                                      transport=httpx.HTTPTransport(local_address="0.0.0.0")
                                  ))
        self.model = settings.MODEL_AI
        self.prompt_prog = load_system_prompt('ai/prog/settings_prog.md')

    async def gpt4(self, question, user_id, chat_topic):
        context = await build_context(user_id, chat_topic, question, self.prompt_prog)
        try:
            response = await self.client.chat.completions.create(
                messages=context,
                model=self.model
            )
            return response.choices[0].message.content
        except Exception as e:
            logging.error(f"Error during OpenAI request:\n {e}")
            return "Произошла ошибка при обработке запроса."