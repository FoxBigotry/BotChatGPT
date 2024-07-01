from pydantic import BaseModel, Field


class UserModel(BaseModel):
    user_id: str
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None


class MessageModel(BaseModel):
    user_id: str
    datetime: str | None = Field(None)
    message: str | None = Field(None)
    response: str | None = Field(None)
    chat_topic: str | None = Field(None)


class RecipeModel(BaseModel):
    user_id: str
    recipe: str | None = Field(None)