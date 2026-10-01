from __future__ import annotations
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.db.models import CreditLedger, User, Referral

async def get_or_create_user(
    session: AsyncSession,
    telegram_user_id: int,
    username: str | None,
    first_name: str | None,
) -> tuple[User, bool]:
    result = await session.execute(select(User).where(User.telegram_user_id == telegram_user_id))
    user = result.scalar_one_or_none()
    now = datetime.now(timezone.utc)
    if user:
        user.username = username
        user.first_name = first_name
        user.last_active_at = now
        await session.commit()
        return user, False

    user = User(
        telegram_user_id=telegram_user_id,
        username=username,
        first_name=first_name,
        credits=settings.free_credits,
        last_active_at=now,
    )
    session.add(user)
    await session.flush()
    session.add(CreditLedger(user_id=user.id, amount=settings.free_credits, reason="signup"))
    await session.commit()
    return user, True

async def add_credits(session: AsyncSession, user: User, amount: int, reason: str, reference_id: str | None = None):
    if amount <= 0:
        raise ValueError("amount must be positive")
    user.credits += amount
    session.add(CreditLedger(user_id=user.id, amount=amount, reason=reason, reference_id=reference_id))
    await session.commit()

async def spend_credits(session: AsyncSession, user: User, amount: int, reason: str, reference_id: str | None = None) -> bool:
    if amount <= 0:
        raise ValueError("amount must be positive")
    if user.credits < amount:
        return False
    user.credits -= amount
    session.add(CreditLedger(user_id=user.id, amount=-amount, reason=reason, reference_id=reference_id))
    await session.commit()
    return True

async def register_referral(
    session: AsyncSession,
    referred_user: User,
    referrer_telegram_id: int,
) -> bool:
    if referred_user.telegram_user_id == referrer_telegram_id:
        return False
    existing = await session.execute(
        select(Referral).where(Referral.referred_user_id == referred_user.id)
    )
    if existing.scalar_one_or_none():
        return False

    result = await session.execute(
        select(User).where(User.telegram_user_id == referrer_telegram_id)
    )
    referrer = result.scalar_one_or_none()
    if not referrer:
        return False

    referred_user.referred_by_id = referrer.id
    ref = Referral(
        referrer_user_id=referrer.id,
        referred_user_id=referred_user.id,
        status="started",
    )
    session.add(ref)
    await session.commit()
    return True

async def qualify_referral_and_reward(session: AsyncSession, referred_user: User) -> bool:
    result = await session.execute(
        select(Referral).where(Referral.referred_user_id == referred_user.id)
    )
    ref = result.scalar_one_or_none()
    if not ref or ref.reward_given:
        return False

    ref.status = "qualified"
    ref.reward_given = True

    referrer = await session.get(User, ref.referrer_user_id)
    if not referrer:
        return False

    referrer.credits += settings.referral_reward
    session.add(
        CreditLedger(
            user_id=referrer.id,
            amount=settings.referral_reward,
            reason="referral_reward",
            reference_id=str(referred_user.telegram_user_id),
        )
    )
    await session.commit()
    return True
