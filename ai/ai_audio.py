import httpx
import logging
from settings import settings
from openai import AsyncOpenAI


async def speech_to_text_recognition(audio_filepath):
    try:
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY,
                             http_client=httpx.AsyncClient(
                                 proxies=settings.PROXY,
                                 transport=httpx.HTTPTransport(local_address="0.0.0.0")
                             ))
        with open(audio_filepath, 'rb') as audio:
            transcript = await client.audio.transcriptions.create(
                model="whisper-1",
                file=audio,
                response_format="text"
            )
            return transcript

    except Exception as e:
        logging.error(f"Error in file retrieving: {e}")
        return None
