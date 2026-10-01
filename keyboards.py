from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✍️ Handwritten Notes", callback_data="handwriting"),
                InlineKeyboardButton(text="📄 PDF Tools", callback_data="pdf_tools"),
            ],
            [
                InlineKeyboardButton(text="🤖 AI Study Tools", callback_data="ai_tools"),
            ],
            [
                InlineKeyboardButton(text="💎 Get Credits", callback_data="credits"),
                InlineKeyboardButton(text="🎁 Invite Friends", callback_data="referral"),
            ],
            [
                InlineKeyboardButton(text="📊 My Usage", callback_data="usage"),
                InlineKeyboardButton(text="❓ Help", callback_data="help"),
            ],
        ]
    )

def upload_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Finish Upload", callback_data="finish_upload")],
            [InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_upload")],
        ]
    )

def operation_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📝 Clean Notes", callback_data="op:clean_notes"),
                InlineKeyboardButton(text="📄 PDF", callback_data="op:pdf"),
            ],
            [
                InlineKeyboardButton(text="📘 DOCX", callback_data="op:docx"),
                InlineKeyboardButton(text="🧠 Summary", callback_data="op:summary"),
            ],
            [
                InlineKeyboardButton(text="❓ MCQs", callback_data="op:mcqs"),
                InlineKeyboardButton(text="🃏 Flashcards", callback_data="op:flashcards"),
            ],
            [InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_upload")],
        ]
    )
