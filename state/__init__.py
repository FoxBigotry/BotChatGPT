from aiogram.fsm.state import State, StatesGroup


class Generate(StatesGroup):
    start_talk = State()
    in_process = State()

