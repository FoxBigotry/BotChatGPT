import aiofiles
import logging


async def read_markdown_file(file_path: str) -> str:
    try:
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as file:
            return await file.read()
    except Exception as e:
        logging.error(f"Error during OpenAI request: {e}")
        print(f"error: {str(e)}")


async def create_chat_context(last_text, prompt_path: str) -> list:
    info = await read_markdown_file(prompt_path)
    context = [{"role": "system", "content": info}]
    counter = 0
    for msg in last_text[::-1]:

        if 'message' in msg and msg['message']:
            context.append({"role": "user", "content": msg['message']})
        if 'response' in msg and msg['response']:
            context.append({"role": "assistant", "content": msg['response']})
        if counter >= 10:
            break
        counter += 1
    return context
