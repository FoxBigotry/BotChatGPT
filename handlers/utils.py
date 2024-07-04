import datetime
from ai.default.ai_default import OpenAi_default
from ai.prog.ai_prog import OpenAi_prog
from ai.cook.ai_cook import OpenAi_cook
from database.connect import MongoDBActions
from database.models import MessageModel, UserModel

openai_client_default = OpenAi_default()
openai_client_prog = OpenAi_prog()
openai_client_cook = OpenAi_cook()
mongo_actions = MongoDBActions()


async def start_message(chat_topic):
    if chat_topic == '14':
        return ('Привет, я повар🧑‍🍳\n'
                'Я могу ответить на любые вопросы по готовке.\n'
                'Так же могу сохранить рецепт если попросите и напомнить уже сохранённые.\n'
                'Знайте, я могу забыть всё по теме по команде /reset\n'
                'Забыть все рецепты которые мы сохранили /reset_recipes\n'
                'И могу забыть всё и во всех темах по команде /reset_all\n'
                'Какой у вас вопрос?\n'
                'О кстати, в соседнем чате сидит программист👨‍💻')
    elif chat_topic == '22':
        return ('Привет, я программист👨‍💻\n'
                'Я могу ответить на любые вопросы по программированию.\n'
                'Знайте, я могу забыть всё по теме по команде /reset\n'
                'И могу забыть всё и во всех темах по команде /reset_all\n'
                'Какой у вас вопрос?\n'
                'О кстати, в соседнем чате сидит повар🧑‍🍳')
    else:
        return ('Ваш ассистент на месте\n'
                'С каким вопросом могу вам помочь?')


async def create_or_get_user(user_id, from_user):
    user_data = await mongo_actions.get_user(user_id)
    if not user_data:
        user_data = UserModel(
            user_id=user_id,
            username=from_user.username,
            first_name=from_user.first_name,
            last_name=from_user.last_name
        )
        await mongo_actions.create_user(user_data)
    return user_data


async def create_message(user_id, message_text, chat_topic):
    message_data = MessageModel(
        user_id=user_id,
        datetime=str(datetime.datetime.now()),
        message=message_text,
        chat_topic=chat_topic
    )
    return await mongo_actions.create_message(message_data)


async def handle_gpt_response(user_id, message_text, chat_topic):
    if chat_topic == '14':
        return await openai_client_cook.gpt4(message_text, user_id, chat_topic)
    elif chat_topic == '22':
        return await openai_client_prog.gpt4(message_text, user_id, chat_topic)
    else:
        return await openai_client_default.gpt4(message_text, user_id, chat_topic)


async def final_answer(user_id, message_text, chat_topic):
    message_id = await create_message(user_id, message_text, chat_topic)
    response = await handle_gpt_response(user_id, message_text, chat_topic)
    return message_id, response


# async def speech_to_text_recognition(mp3_file_path):
#     if chat_topic == '14':
#         return await openai_client_cook.speech_to_text_recognition(mp3_file_path)
#     elif chat_topic == '22':
#         return await openai_client_prog.speech_to_text_recognition(mp3_file_path)
#     else:
#         return await openai_client_default.speech_to_text_recognition(mp3_file_path)
