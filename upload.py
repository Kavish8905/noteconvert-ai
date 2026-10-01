from __future__ import annotations
from pathlib import Path
import uuid
from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from app.bot.states import UploadState
from app.bot.keyboards import upload_menu, operation_menu
from app.config import settings

router = Router()
DATA_DIR = Path("data/uploads")
DATA_DIR.mkdir(parents=True, exist_ok=True)

@router.callback_query(F.data == "handwriting")
async def begin_upload(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(UploadState.collecting)
    await state.update_data(files=[], started_at=str(uuid.uuid4()))
    await callback.message.edit_text(
        "📸 <b>Send your pages</b>\n\n"
        "Send one or more photos. When you're done, press <b>Finish Upload</b>.",
        reply_markup=upload_menu(),
        parse_mode="HTML",
    )
    await callback.answer()

@router.message(UploadState.collecting, F.photo)
async def receive_photo(message: Message, state: FSMContext):
    photo = message.photo[-1]
    max_bytes = settings.max_file_mb * 1024 * 1024
    if photo.file_size and photo.file_size > max_bytes:
        await message.answer(f"⚠️ This image is larger than {settings.max_file_mb} MB.")
        return

    user_dir = DATA_DIR / str(message.from_user.id)
    user_dir.mkdir(parents=True, exist_ok=True)
    path = user_dir / f"{uuid.uuid4().hex}.jpg"

    bot = message.bot
    file = await bot.get_file(photo.file_id)
    await bot.download(file, destination=path)

    data = await state.get_data()
    files = data.get("files", [])
    files.append(str(path))
    await state.update_data(files=files)

    await message.answer(
        f"✅ Page {len(files)} received.\n"
        "Add more pages or press <b>Finish Upload</b>.",
        reply_markup=upload_menu(),
        parse_mode="HTML",
    )

@router.callback_query(UploadState.collecting, F.data == "finish_upload")
async def finish_upload(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    files = data.get("files", [])
    if not files:
        await callback.answer("Send at least one image first.", show_alert=True)
        return
    await state.set_state(UploadState.choosing_operation)
    await callback.message.edit_text(
        f"✅ <b>{len(files)} pages received.</b>\n\nWhat do you want to create?",
        reply_markup=operation_menu(),
        parse_mode="HTML",
    )
    await callback.answer()

@router.callback_query(F.data == "cancel_upload")
async def cancel_upload(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    for path in data.get("files", []):
        Path(path).unlink(missing_ok=True)
    await state.clear()
    await callback.message.edit_text(
        "Upload cancelled.\n\nUse the menu to start again.",
    )
    await callback.answer()
