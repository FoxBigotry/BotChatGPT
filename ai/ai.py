import httpx
import logging
from ai.context import create_chat_context
from settings import settings
from openai import AsyncOpenAI
from database.connect import MongoDBActions


mongo_actions = MongoDBActions()


class OpenAi:
    def __init__(self, default_model: str = settings.DEFAULT_MODEL, prompt_path: str = 'ai/uni_agent.md'):
        if settings.PROXY:
            self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY,
                                      http_client=httpx.AsyncClient(
                                          proxies=settings.PROXY,
                                          transport=httpx.HTTPTransport(local_address="0.0.0.0")
                                      ))
        else:
            self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

        self.agent_system_prompt = self.load_system_prompt(prompt_path)
        self.default_model = default_model

    @staticmethod
    def load_system_prompt(prompt_path: str) -> str:
        """
        Load the system prompt from a file.
        """
        with open(prompt_path, 'r', encoding='utf-8') as file:
            return file.read()


    async def gpt4(self, question, user_id, prompt_path: str = 'ai/settings.md'):
        last_text = await mongo_actions.get_user_messages(user_id)
        context = await create_chat_context(last_text, prompt_path)
        # context.append({"role": "user", "content": str(question)})
        # full_prompt = [{"role": "system", "content": self.agent_system_prompt}]
        # for message in last_text[-settings.HISTORY_LENGTH:]:
        #     full_prompt.append({"role": message.msg_type, "content": message.text})
        try:
            response = await self.client.chat.completions.create(
                messages=context,
                model=settings.DEFAULT_MODEL,
                temperature=settings.DEFAULT_TEMPERATURE,
            )
            return response
        except Exception as e:
            logging.error(f"Error during OpenAI request: {e}")
            print(f"error: {str(e)}")

    async def speech_to_text_recognition(self, audio_filepath):
        try:
            with open(audio_filepath, 'rb') as audio:
                transcript = await self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio,
                    response_format="text"
                )
                return transcript

        except Exception as e:
            print(f"Error in file retrieving: {e}\n{e.__str__()}")

    # async def generate_response(self, thread_id: str, **kwargs):
    #     """
    #     Generate a response from the OpenAI API using the system prompt combined with the user's prompt,
    #     optionally using a specified model or the default model.
    #
    #     :param thread_id: The thread ID to use for generating the response.
    #     :param kwargs: Additional parameters to pass to the OpenAI API call.
    #     :return: The generated text response.
    #     """
    #
    #     user_data = await db.get_user_data(thread_id)
    #     user_history = await db.get_history(thread_id)
    #     full_system_prompt = (f"""{self.agent_system_prompt}\n
    #                           Information about user, based on old conversation and user_language to speak in:\n
    #                           {user_data}""")
    #     full_prompt = [{"role": "system", "content": full_system_prompt}]
    #     print(full_prompt)
    #     for message in user_history[-settings.HISTORY_LIMIT:]:  # last N messages
    #         full_prompt.append({"role": message.msg_type, "content": message.text})
    #
    #     response = self.client.chat.completions.create(
    #         model=self.default_model,
    #         messages=full_prompt,
    #         temperature=1,
    #         )
    #
    #     logger.info(f"Response generated: {response}")
    #     agent_message = BaseTgMessage.from_openai_message(response, "assistant", thread_id=thread_id)
    #
    #     return agent_message