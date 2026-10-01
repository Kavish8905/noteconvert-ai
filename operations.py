from __future__ import annotations
from pathlib import Path
from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from app.bot.states import UploadState
from app.config import settings
from app.db.models import Job, User
from app.db.session import SessionLocal
from app.services.ai_tools import generate_from_text
from app.services.document import create_docx, create_pdf
from app.services.ocr import transcribe
from app.services.users import spend_credits, qualify_referral_and_reward

router = Router()

COSTS = {
    "clean_notes": 2,
    "pdf": 1,
    "docx": 1,
    "summary": 2,
    "mcqs": 3,
    "flashcards": 3,
}

async def get_user(session, telegram_user_id: int) -> User:
    result = await session.execute(
        select(User).where(User.telegram_user_id == telegram_user_id)
    )
    user = result.scalar_one()
    return user

@router.callback_query(UploadState.choosing_operation, F.data.startswith("op:"))
async def run_operation(callback: CallbackQuery, state: FSMContext):
    operation = callback.data.split(":", 1)[1]
    cost = COSTS[operation]
    data = await state.get_data()
    files = [Path(p) for p in data.get("files", [])]

    async with SessionLocal() as session:
        user = await get_user(session, callback.from_user.id)
        if user.is_banned:
            await callback.message.edit_text("Your account is restricted.")
            await state.clear()
            return
        if not await spend_credits(session, user, cost, reason=operation):
            await callback.message.edit_text(
                f"❌ Not enough credits.\n\n"
                f"This operation costs <b>{cost}</b> credits.\n"
                f"You have <b>{user.credits}</b>.\n\n"
                f"Use /start to return to the menu.",
                parse_mode="HTML",
            )
            await state.clear()
            return

        job = Job(user_id=user.id, job_type=operation, status="processing", credits_used=cost)
        session.add(job)
        await session.commit()
        job_id = job.id

    await callback.answer()
    await callback.message.edit_text(
        f"🔄 Processing <b>{len(files)} page(s)</b>…",
        parse_mode="HTML",
    )

    try:
        chunks: list[str] = []
        for path in files:
            chunks.append(await transcribe(path))
        raw_text = "\n\n".join(chunks).strip()

        if not raw_text:
            raise RuntimeError("No readable text was detected.")

        if operation == "clean_notes":
            result_text = await generate_from_text(raw_text, "clean_notes")
        elif operation in {"summary", "mcqs", "flashcards"}:
            result_text = await generate_from_text(raw_text, operation)
        else:
            result_text = raw_text

        output_dir = Path("data/results")
        output_dir.mkdir(parents=True, exist_ok=True)

        if operation == "docx":
            output_path = output_dir / f"notes_{job_id}.docx"
            create_docx(result_text, output_path)
            await callback.message.answer_document(
                document=output_path.open("rb"),
                caption="📘 Your editable DOCX is ready.",
            )
        elif operation == "pdf":
            output_path = output_dir / f"notes_{job_id}.pdf"
            create_pdf(result_text, output_path)
            await callback.message.answer_document(
                document=output_path.open("rb"),
                caption="📄 Your PDF is ready.",
            )
        else:
            # Send text first; user can then choose PDF/DOCX in later iterations.
            await callback.message.answer(
                f"✅ <b>Done</b>\n\n{result_text[:3800]}",
                parse_mode="HTML",
            )

        async with SessionLocal() as session:
            db_job = await session.get(Job, job_id)
            if db_job:
                db_job.status = "completed"
                await session.commit()
            user = await get_user(session, callback.from_user.id)
            # Referral becomes qualified after first successful paid-cost operation.
            await qualify_referral_and_reward(session, user)

    except Exception as exc:
        async with SessionLocal() as session:
            db_job = await session.get(Job, job_id)
            if db_job:
                db_job.status = "failed"
                db_job.error_message = str(exc)[:1000]
                # Refund on failed processing.
                user = await get_user(session, callback.from_user.id)
                user.credits += cost
                session.add(
                    __import__("app.db.models", fromlist=["CreditLedger"]).CreditLedger(
                        user_id=user.id,
                        amount=cost,
                        reason="failed_job_refund",
                        reference_id=str(job_id),
                    )
                )
                await session.commit()
        await callback.message.answer(
            "⚠️ Processing failed.\n\n"
            "Your credits were refunded. Please try again with a clearer image."
        )
    finally:
        for path in files:
            path.unlink(missing_ok=True)
        await state.clear()
