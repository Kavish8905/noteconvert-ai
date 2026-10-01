from aiogram.fsm.state import State, StatesGroup

class UploadState(StatesGroup):
    collecting = State()
    choosing_operation = State()
