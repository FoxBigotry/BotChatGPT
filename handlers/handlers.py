import logging
import datetime
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from ai.ai import OpenAi
from database.connect import MongoDBActions
from database.modeles import MessageModel, UserModel

router = Router()
openai_client = OpenAi()
mongo_actions = MongoDBActions()

user_states = {}


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer('Бот поднялся\n'
                         'Какой у вас вопрос для великого разума?\n'
                         'Знай, я могу забыть всё по коменде /reset')


@router.message(Command("reset"))
async def cmd_reset(message: Message):
    await mongo_actions.reset_all(str(message.from_user.id))
    await message.answer('Всё было удалено, если хочешь мы можем начать сначала.')


@router.message(F.text)
async def handle_message(message: Message):
    user_id = str(message.from_user.id)
    message_text = message.text

    user_data = await mongo_actions.get_user(user_id)
    if not user_data:
        user_data = UserModel(
            user_id=user_id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name
        )
        await mongo_actions.create_user(user_data)

    if user_id in user_states:
        user_states[user_id] = message_text
        await message.answer("Что ж, думаю над новым вопросом...")
    else:
        user_states[user_id] = message_text
        await message.answer("Думаю над вопросом...")

        try:
            message_data = MessageModel(
                user_id=user_id,
                datetime=str(datetime.datetime.now()),
                message=message_text
                )
            message_id = await mongo_actions.create_message(message_data)

            response = await openai_client.gpt4(message_text, user_id)

            if user_id in user_states and user_states[user_id] != message_text:
                message_text = user_states[user_id]
                message_data = MessageModel(
                    user_id=user_id,
                    datetime=str(datetime.datetime.now()),
                    message=message_text
                    )
                message_id = await mongo_actions.create_message(message_data)
                response = await openai_client.gpt4(message_text, user_id)

            update_data = {"response": response.choices[0].message.content}
            await mongo_actions.update_message(message_id, update_data)
            await message.answer(response.choices[0].message.content)

        except Exception as e:
            logging.error(f"Error while saving to MongoDB: {e}")
            await message.answer("An error occurred while saving your message.")

        finally:
            if user_id in user_states:
                del user_states[user_id]
