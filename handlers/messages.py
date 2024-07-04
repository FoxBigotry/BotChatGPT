import logging
from aiogram import Router, F
from aiogram.types import Message, ContentType
from database.connect import MongoDBActions
from handlers.utils import create_or_get_user, final_answer
from settings import settings
from handlers.voice_processing import generate_unique_name, convert_ogg_to_mp3, delete_file_by_file_path
from ai.ai_audio import speech_to_text_recognition

router_message = Router()
mongo_actions = MongoDBActions()
user_states = {}


@router_message.message(F.text)
async def handle_message(message: Message, voice_msg_text=None):
    user_id = str(message.from_user.id)
    chat_topic = str(message.message_thread_id)

    if user_id not in settings.USER_IDS.split(','):
        await message.answer("Я персональный ассистент для узкого круга лиц.\n "
                             "Можете написать @astehr для получения доступа ")
        return

    await create_or_get_user(user_id, message.from_user)

    if voice_msg_text:
        message_text = voice_msg_text
    else:
        message_text = message.text

    if user_id in user_states:
        user_states[user_id] = message_text
        waiting_msg = await message.answer("Что ж, думаю над новым вопросом...")
    else:
        user_states[user_id] = message_text
        waiting_msg = await message.answer("Думаю над вопросом...")

        try:
            message_id, response = await final_answer(user_id, message_text, chat_topic)

            if user_id in user_states and user_states[user_id] != message_text:
                message_text = user_states[user_id]
                message_id, response = await final_answer(user_id, message_text, chat_topic)

            update_data = {"response": response}
            await mongo_actions.update_message(message_id, update_data)
            await waiting_msg.delete()
            await message.answer(response)
        except Exception as e:
            logging.error(f"Error while saving to MongoDB:\n {e}")
            await message.answer("Произошла ошибка при сохранении вашего сообщения.")

        finally:
            if user_id in user_states:
                del user_states[user_id]


@router_message.message()
async def handle_voice(message: Message):
    if message.content_type == ContentType.VOICE:
        chat_topic = str(message.message_thread_id)
        file_uuid = generate_unique_name()
        ogg_file_path = settings.AUDIOS_DIR + f"{file_uuid}.ogg"
        mp3_file_path = settings.AUDIOS_DIR + f"{file_uuid}.mp3"

        with open(ogg_file_path, 'wb') as voice_ogg:
            file_id = message.voice.file_id
            file = await message.bot.get_file(file_id)
            file_path = file.file_path
            voice_data = await message.bot.download_file(file_path)
            voice_ogg.write(voice_data.read())
        try:
            convert_ogg_to_mp3(ogg_file_path, mp3_file_path)
            transcript = await speech_to_text_recognition(mp3_file_path)
        except Exception as e:
            print(f"Error in speech to text recognition: {e.__str__()}")
            transcript = None

        if transcript is None:
            await message.reply("Не смог распознать голосовое сообщение :c")
        else:
            delete_file_by_file_path(ogg_file_path)
            delete_file_by_file_path(mp3_file_path)
            await handle_message(message, voice_msg_text=transcript)

    else:
        # system_messages = await get_system_messages(str(message.chat.id))
        # # FIXME:test
        # await message.reply(system_messages.cant_handle)
        await message.reply("Не могу обработать данное сообщение")
