import logging
from database.connect import MongoDBActions

mongo_actions = MongoDBActions()


def load_system_prompt(prompt_path: str) -> str:
    try:
        with open(prompt_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        logging.error(f"Error open MD file:\n {e}")


async def create_chat_context(last_text) -> list:
    context = []

    for msg in last_text:
        if 'message' in msg and msg['message']:
            context.append({"role": "user", "content": msg['message']})
        if 'response' in msg and msg['response']:
            context.append({"role": "assistant", "content": msg['response']})
    return context


async def build_context(user_id, chat_topic, question, prompt):
    context = [{"role": "system", "content": prompt}]
    last_text = await mongo_actions.get_user_messages(user_id, chat_topic)
    context_user = await create_chat_context(last_text)
    context.extend(context_user)
    context.append({"role": "user", "content": str(question)})
    return context


# async def create_chat_context(last_text, prompt_path: str) -> list:
#     info = await read_markdown_file(prompt_path)
#     context = [{"role": "system", "content": info}]
#     counter = 0
#     for msg in last_text[::-1]:
#
#         if 'message' in msg and msg['message']:
#             context.append({"role": "user", "content": msg['message']})
#         if 'response' in msg and msg['response']:
#             context.append({"role": "assistant", "content": msg['response']})
#         if counter >= 10:
#             break
#         counter += 1
#     return context
