from datetime import datetime
from typing import Self

from pydantic import BaseModel, Field
from openai.types.chat import ChatCompletion

from ai.utils import BaseUtils


class UserModel(BaseModel):

    user_id: str
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None


class MessageModel(BaseModel):
    user_id: str
    username: str | None = Field(None)
    first_name: str | None = Field(None)
    last_name: str | None = Field(None)
    datetime: str | None = Field(None)
    message: str | None = Field(None)
    response: str | None = Field(None)

    prompt_tokens: int | None = Field(None)
    completion_tokens: int | None = Field(None)
    spent_tokens: int | None = Field(None)
    token_price: float | None = Field(None)


    @classmethod
    def from_openai_message(cls, response: ChatCompletion, msg_type: str, thread_id: str) -> Self:
        utils = BaseUtils()
        rounded_token_price = utils.token_price(response)

        # convert date to isoformat
        dt_object = datetime.fromtimestamp(response.created)
        iso_format_date = dt_object.isoformat()

        return cls(
            message=response.choices[0].message.content.strip(),
            datetime=iso_format_date,
            user_id=thread_id,
            prompt_tokens=response.usage.prompt_tokens,
            completion_tokens=response.usage.completion_tokens,
            spent_tokens=response.usage.total_tokens,
            token_price=rounded_token_price,
        )