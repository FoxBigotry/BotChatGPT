from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from database.connect import MongoDBActions
from handlers.utils import start_message

router_command = Router()
mongo_actions = MongoDBActions()


@router_command.message(CommandStart())
async def cmd_start(message: Message):
    chat_topic = str(message.message_thread_id)
    answer = await start_message(chat_topic)
    await message.answer(answer)


@router_command.message(Command("reset_all"))
async def cmd_reset(message: Message):
    await mongo_actions.reset_all(str(message.from_user.id))
    await message.answer('Всё было удалено, если хочешь мы можем начать сначала.')


@router_command.message(Command("reset"))
async def cmd_reset(message: Message):
    await mongo_actions.reset_topic(str(message.from_user.id), str(message.message_thread_id))
    await message.answer('Твоя история в этой теме была удалена, если хочешь мы можем начать сначала.')


@router_command.message(Command("reset_recipes"))
async def cmd_reset(message: Message):
    await mongo_actions.reset_recipes(str(message.from_user.id))
    await message.answer('Все сохранённые рецепты удалены,')
