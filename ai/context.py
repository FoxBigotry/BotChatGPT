import aiofiles
import logging


async def read_markdown_file(file_path: str) -> str:
    try:
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as file:
            return await file.read()
    except Exception as e:
        logging.error(f"Error open MD file:\n {e}")


async def create_chat_context(last_text, chat_topic) -> list:
    context = []

    for msg in last_text:
        if 'message' in msg and msg['message']:
            context.append({"role": "user", "content": msg['message']})
        if 'response' in msg and msg['response']:
            context.append({"role": "assistant", "content": msg['response']})
    return context
