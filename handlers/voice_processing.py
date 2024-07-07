import os
import uuid

from moviepy.editor import AudioFileClip

from settings import settings


def convert_ogg_to_mp3(ogg_file_path: str, mp3_file_path: str):
    try:
        audio = AudioFileClip(ogg_file_path)
        audio.write_audiofile(mp3_file_path)
    except Exception as e:
        print(f"Error converting ogg to mp3: {e}")


async def download_voice_as_ogg(voice):
    voice_file = await voice.get_file()
    ogg_filepath = os.path.join(settings.AUDIOS_DIR, f"{generate_unique_name()}.ogg")
    await voice_file.download_to_drive(ogg_filepath)
    return ogg_filepath


def generate_unique_name():
    return str(uuid.uuid4())


def delete_file_by_file_path(file_path: str):
    try:
        os.remove(file_path)
        print(f"File '{file_path}' has been deleted.")
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
    except PermissionError:
        print(f"Permission denied to delete file '{file_path}'.")
    except Exception as e:
        print(f"Error deleting file '{file_path}': \n{e}")
