import logging
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from settings import settings
from database.modeles import MessageModel, UserModel


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

    user_model = UserModel
    message_model = MessageModel

    async def reset_all(self, user_id: str):
        try:
            await self.message_collection.delete_many({"user_id": user_id})
            await self.users_collection.delete_many({"user_id": user_id})
        except Exception as e:
            logging.error(f"Error while resetting data: {e}")

    async def get_user_messages(self, user_id: str, limit=settings.HISTORY_LENGTH):
        try:
            messages = await (
                self.message_collection.find({'user_id': user_id})
                .sort('datetime', -1)
                .limit(limit)
                .to_list(length=limit)
            )
            if not messages:
                return []
            return messages
        except Exception as e:
            logging.error(f"Error while getting user messages: {e}")
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
            logging.error(f"Error while getting user data: {e}")
            return None
