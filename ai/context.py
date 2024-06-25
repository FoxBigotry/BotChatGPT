import aiofiles
import logging


async def read_markdown_file(file_path: str) -> str:
    try:
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as file:
            return await file.read()
    except Exception as e:
        logging.error(f"Error during OpenAI request: {e}")
        print(f"error: {str(e)}")


async def create_chat_context(last_text, chat_topic) -> list:

    if chat_topic == '14':
        info = await read_markdown_file('ai/settings.md')
        context = [{"role": "system", "content": info}]
    elif chat_topic == '22':
        info = await read_markdown_file('ai/settings_prog.md')
        context = [{"role": "system", "content": info}]
    else:
        default_info = "Default system information"
        context = [{"role": "system", "content": default_info}]

    for msg in last_text:
        if 'message' in msg and msg['message']:
            context.append({"role": "user", "content": msg['message']})
        if 'response' in msg and msg['response']:
            context.append({"role": "assistant", "content": msg['response']})
    return context
