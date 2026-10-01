from __future__ import annotations
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from app.db.session import SessionLocal
from app.services.users import get_or_create_user, register_referral
from app.bot.keyboards import main_menu

router = Router()

@router.message(CommandStart())
async def start_handler(message: Message) -> None:
    args = message.text.split(maxsplit=1)
    referral_arg = args[1] if len(args) > 1 else None

    async with SessionLocal() as session:
        user, created = await get_or_create_user(
            session,
            message.from_user.id,
            message.from_user.username,
            message.from_user.first_name,
        )
        if created and referral_arg and referral_arg.startswith("ref_"):
            try:
                referrer_id = int(referral_arg.removeprefix("ref_"))
                await register_referral(session, user, referrer_id)
            except ValueError:
                pass

    await message.answer(
        f"👋 <b>Welcome to NoteConvert AI</b>\n\n"
        f"Turn handwritten notes and documents into clean digital study material.\n\n"
        f"🎁 You have <b>{user.credits} free credits</b>.\n\n"
        f"Send your notes as photos to get started.",
        reply_markup=main_menu(),
        parse_mode="HTML",
    )
