import logging
import datetime
from aiogram import Router, F
from aiogram.types import Message, ContentType
from aiogram.filters import CommandStart, Command
from ai.ai import OpenAi
from database.connect import MongoDBActions
from database.modeles import MessageModel, UserModel
from handlers.voice_processing import generate_unique_name, convert_ogg_to_mp3, delete_file_by_file_path
from settings import settings

router = Router()
openai_client = OpenAi()
mongo_actions = MongoDBActions()

user_states = {}


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer('Ваш ассистент на месте\n'
                         'С каким вопросом могу вам помочь?')


@router.message(Command("reset_dev"))
async def cmd_reset(message: Message):
    await mongo_actions.reset_all(str(message.from_user.id))
    await message.answer('Всё было удалено, если хочешь мы можем начать сначала.')


@router.message(F.text)
async def handle_message(message: Message, voice_msg_text=None):
    user_id = str(message.from_user.id)
    if user_id not in settings.USER_IDS.split(','):
        await message.answer("Я персональный ассистент для узкого круга лиц.\n "
                             "Можете написать @astehr для получения доступа ")
        return

    if voice_msg_text:
        message_text = voice_msg_text
    else:
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
        waiting_msg = await message.answer("Что ж, думаю над новым вопросом...")
    else:
        user_states[user_id] = message_text
        waiting_msg = await message.answer("Думаю над вопросом...")

        try:
            message_data = MessageModel(
                user_id=user_id,
                datetime=str(datetime.datetime.now()),
                message=message_text
                )
            message_id = await mongo_actions.create_message(message_data)

            response = await openai_client.gpt4(message_text, user_id, 'ai/uni_agent.md')

            if user_id in user_states and user_states[user_id] != message_text:
                message_text = user_states[user_id]
                message_data = MessageModel(
                    user_id=user_id,
                    datetime=str(datetime.datetime.now()),
                    message=message_text
                    )
                message_id = await mongo_actions.create_message(message_data)
                response = await openai_client.gpt4(message_text, user_id, 'ai/uni_agent.md')

            update_data = {"response": response.choices[0].message.content}
            await mongo_actions.update_message(message_id, update_data)
            await waiting_msg.delete()
            await message.answer(response.choices[0].message.content)

        except Exception as e:
            logging.error(f"Error while saving to MongoDB: {e}")
            await message.answer("An error occurred while saving your message.")

        finally:
            if user_id in user_states:
                del user_states[user_id]


@router.message()
async def handle_voice(message: Message):
    if message.content_type == ContentType.VOICE:
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
            transcript = await openai_client.speech_to_text_recognition(mp3_file_path)
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
        system_messages = await get_system_messages(str(message.chat.id))
        # FIXME:test
        await message.reply(system_messages.cant_handle)