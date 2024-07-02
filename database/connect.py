import logging
import random
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from settings import settings
from database.models import MessageModel, UserModel, RecipeModel


class MongoDBConnection:
    def __init__(self):
        self.cluster = AsyncIOMotorClient(settings.MONGO_URI)
        self.db = self.cluster[settings.MONGO_DB_NAME]


class MongoDBActions(MongoDBConnection):
    @property
    def users_collection(self) -> AsyncIOMotorCollection:
        return self.db["users"]

    @property
    def message_collection(self) -> AsyncIOMotorCollection:
        return self.db["messages"]

    @property
    def favorite_recipes_collection(self) -> AsyncIOMotorCollection:
        return self.db["favorite_recipes"]

    user_model = UserModel
    message_model = MessageModel
    favorite_recipes_model = RecipeModel

    async def reset_all(self, user_id: str):
        try:
            await self.message_collection.delete_many({"user_id": user_id})
            await self.users_collection.delete_many({"user_id": user_id})
            await self.favorite_recipes_collection.delete_many({"user_id": user_id})
        except Exception as e:
            logging.error(f"Error while resetting all data:\n {e}")

    async def get_user_messages(self, user_id: str, chat_topic: str, limit=5):
        try:
            messages = await self.message_collection.find({'user_id': user_id,
                                                           'chat_topic': chat_topic}
                                                          ).sort('datetime',
                                                                 -1).limit(limit).to_list(length=limit)
            if not messages:
                return []
            messages.sort(key=lambda x: x['datetime'])
            return messages
        except Exception as e:
            logging.error(f"Error while getting user messages:\n {e}")
            return []

    async def create_message(self, message_data: MessageModel):
        data = message_data.dict(by_alias=True)
        result = await self.message_collection.insert_one(data)
        return str(result.inserted_id)

    async def update_message(self, message_id, new_data):
        await self.message_collection.update_one(
            {"_id": ObjectId(message_id)},
            {"$set": new_data}
        )

    async def create_user(self, user_data: UserModel):
        data = user_data.dict(by_alias=True)
        result = await self.users_collection.insert_one(data)
        return str(result.inserted_id)

    async def get_user(self, user_id: str):
        try:
            user = await self.users_collection.find_one({"user_id": user_id})
            return user
        except Exception as e:
            logging.error(f"Error while getting user data:\n {e}")
            return None

    async def reset_topic(self, user_id: str, chat_topic: str):
        try:
            await self.message_collection.delete_many({"user_id": user_id,
                                                       "chat_topic": chat_topic})
        except Exception as e:
            logging.error(f"Error while resetting topic data:\n {e}")

    async def save_favorite_recipes(self, user_id: str, recipe: str):
        recipe_data = RecipeModel(
            user_id=user_id,
            recipe=recipe
        )
        try:
            await self.favorite_recipes_collection.insert_one(recipe_data.dict())
        except Exception as e:
            logging.error(f"Error while saving recipe data:\n {e}")

    async def get_favorite_recipes(self, user_id: str):
        try:
            cursor = self.favorite_recipes_collection.find({"user_id": user_id})
            recipes = await cursor.to_list(length=None)
            if recipes:
                random_recipe = random.choice(recipes)
                return random_recipe["recipe"]
            else:
                return 'Нет записей для данного пользователя'
        except Exception as e:
            logging.error(f"Error while collecting recipe data:\n {e}")

    async def reset_recipes(self, user_id: str):
        try:
            await self.favorite_recipes_collection.delete_many({"user_id": user_id})
        except Exception as e:
            logging.error(f"Error while resetting recipe data:\n {e}")
