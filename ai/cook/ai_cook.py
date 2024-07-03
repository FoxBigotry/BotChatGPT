import json
import httpx
import logging
from ai.context import load_system_prompt, build_context
from settings import settings
from openai import AsyncOpenAI
from database.connect import MongoDBActions
from pydantic import BaseModel


mongo_actions = MongoDBActions()


class FavoriteRecipes(BaseModel):
    recipe: str


class OpenAi_cook:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY,
                                  http_client=httpx.AsyncClient(
                                      proxies=settings.PROXY,
                                      transport=httpx.HTTPTransport(local_address="0.0.0.0")
                                  ))
        self.model = settings.MODEL_AI
        self.prompt_cook = load_system_prompt('ai/cook/settings_cook.md')

    tools = [
        {
            "type": "function",
            "function": {
                "name": "save_favorite_recipes",
                "description": "If the user asked to save the recipe",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "favorite_recipes": {
                            "type": "object",
                            "properties": {
                                "recipe": {
                                    "type": "string",
                                    "description": "Favorite recipes",
                                }
                            },
                            "required": ["recipe"]
                        }
                    },
                    "required": ["favorite_recipes"]
                },
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_favorite_recipes",
                "description": "If the user asks for saved recipes",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "The user's ID"
                        }
                    },
                    "required": ["user_id"]
                }
            }
        }]

    async def gpt4(self, question, user_id, chat_topic):
        context = await build_context(user_id, chat_topic, question, self.prompt_cook)
        try:
            response = await self.client.chat.completions.create(
                messages=context,
                model=self.model,
                tools=self.tools
            )

            if response.choices[0].message.tool_calls:
                for call in response.choices[0].message.tool_calls:
                    function_name = call.function.name
                    arguments_dict = json.loads(call.function.arguments)

                    if function_name == "save_favorite_recipes":
                        favorite_recipes = arguments_dict["favorite_recipes"]
                        await mongo_actions.save_favorite_recipes(user_id, favorite_recipes['recipe'])
                        return "сохранено"
                    elif function_name == "get_favorite_recipes":
                        random_recipe = await mongo_actions.get_favorite_recipes(user_id)
                        return random_recipe
            return response.choices[0].message.content

        except Exception as e:
            logging.error(f"Error during OpenAI request:\n {e}")
