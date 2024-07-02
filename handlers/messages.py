import logging
from aiogram import Router, F
from aiogram.types import Message
from database.connect import MongoDBActions
from handlers.utils import create_or_get_user, final_answer

router_message = Router()
mongo_actions = MongoDBActions()
user_states = {}


@router_message.message(F.text)
async def handle_message(message: Message):
    user_id = str(message.from_user.id)
    message_text = message.text
    chat_topic = str(message.message_thread_id)
    await create_or_get_user(user_id, message.from_user)

    if user_id in user_states:
        user_states[user_id] = message_text
        await message.answer("Что ж, думаю над новым вопросом...")
    else:
        user_states[user_id] = message_text
        await message.answer("Думаю над вопросом...")

        try:
            message_id, response = await final_answer(user_id, message_text, chat_topic)

            if user_id in user_states and user_states[user_id] != message_text:
                message_text = user_states[user_id]
                message_id, response = await final_answer(user_id, message_text, chat_topic)

            update_data = {"response": response}
            await mongo_actions.update_message(message_id, update_data)
            await message.answer(response)
        except Exception as e:
            logging.error(f"Error while saving to MongoDB:\n {e}")
            await message.answer("Произошла ошибка при сохранении вашего сообщения.")

        finally:
            if user_id in user_states:
                del user_states[user_id]
