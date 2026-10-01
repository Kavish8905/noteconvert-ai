from __future__ import annotations
from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from app.bot.keyboards import main_menu
from app.config import settings
from app.db.models import User, CreditLedger
from app.db.session import SessionLocal
from sqlalchemy import select, func

router = Router()

@router.callback_query(F.data == "credits")
async def credits(callback: CallbackQuery):
    await callback.message.edit_text(
        "💎 <b>Credit packs</b>\n\n"
        "Payment integration is prepared for the next build stage.\n"
        "For now, use your free/referral credits.",
        reply_markup=main_menu(),
        parse_mode="HTML",
    )
    await callback.answer()

@router.callback_query(F.data == "referral")
async def referral(callback: CallbackQuery):
    me = await callback.bot.get_me()
    link = f"https://t.me/{me.username}?start=ref_{callback.from_user.id}"
    await callback.message.edit_text(
        "🎁 <b>Invite Friends</b>\n\n"
        f"Share this link:\n<code>{link}</code>\n\n"
        f"Earn <b>+{settings.referral_reward} credits</b> when a referred user completes their first successful operation.",
        reply_markup=main_menu(),
        parse_mode="HTML",
    )
    await callback.answer()

@router.callback_query(F.data == "usage")
async def usage(callback: CallbackQuery):
    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_user_id == callback.from_user.id)
        )
        user = result.scalar_one()
    await callback.message.edit_text(
        f"📊 <b>Your usage</b>\n\n"
        f"Credits remaining: <b>{user.credits}</b>\n\n"
        "More detailed analytics will be added in the admin dashboard.",
        reply_markup=main_menu(),
        parse_mode="HTML",
    )
    await callback.answer()

@router.callback_query(F.data == "help")
async def help_handler(callback: CallbackQuery):
    await callback.message.edit_text(
        "❓ <b>How to use</b>\n\n"
        "1. Tap Handwritten Notes.\n"
        "2. Send one or more page photos.\n"
        "3. Press Finish Upload.\n"
        "4. Choose what you want to create.\n\n"
        "For best results, use sharp, well-lit pages.",
        reply_markup=main_menu(),
        parse_mode="HTML",
    )
    await callback.answer()

@router.message(F.text == "/credits")
async def credits_command(message: Message):
    await message.answer("Use the 💎 Get Credits button from the main menu.")

@router.message(F.text == "/help")
async def help_command(message: Message):
    await message.answer(
        "Send /start to open NoteConvert AI."
    )
