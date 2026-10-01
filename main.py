from __future__ import annotations
import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiohttp import web

from app.config import settings
from app.db.session import init_db
from app.bot.handlers.start import router as start_router
from app.bot.handlers.upload import router as upload_router
from app.bot.handlers.operations import router as operations_router
from app.bot.handlers.general import router as general_router


logging.basicConfig(level=logging.INFO)


async def main() -> None:
    await init_db()

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    dp.include_router(start_router)
    dp.include_router(upload_router)
    dp.include_router(operations_router)
    dp.include_router(general_router)

    await bot.delete_webhook(drop_pending_updates=True)

    async def health(request):
        return web.Response(text="NoteConvert AI is running")

    app = web.Application()
    app.router.add_get("/", health)

    runner = web.AppRunner(app)
    await runner.setup()

    port = int(os.getenv("PORT", "10000"))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    logging.info(f"Health server listening on port {port}")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
