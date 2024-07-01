import httpx
import logging
from ai.context import create_chat_context, read_markdown_file
from settings import settings
from openai import AsyncOpenAI
from database.connect import MongoDBActions


mongo_actions = MongoDBActions()


class OpenAi_prog:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY,
                                  http_client=httpx.AsyncClient(
                                      proxies=settings.PROXY,
                                      transport=httpx.HTTPTransport(local_address="0.0.0.0")
                                  ))
        self.model = settings.MODEL_AI
        self.prompt_prog = None

    async def initialize_prompt(self):
        self.prompt_prog = await read_markdown_file('ai/prog/settings_prog.md')

    async def gpt4(self, question, user_id, chat_topic):
        if self.prompt_prog is None:
            await self.initialize_prompt()
        context = [{"role": "system", "content": self.prompt_prog}]
        last_text = await mongo_actions.get_user_messages(user_id, chat_topic)
        context_user = await create_chat_context(last_text, chat_topic)
        context.extend(context_user)
        print(context)
        context.append({"role": "user", "content": str(question)})
        try:
            response = await self.client.chat.completions.create(
                messages=context,
                model=self.model
            )
            return response.choices[0].message.content
        except Exception as e:
            logging.error(f"Error during OpenAI request:\n {e}")
