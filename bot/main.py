"""QuietSpace Tashkent bot entrypoint."""
import argparse
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import (
    BOT_WEBHOOK_HOST,
    BOT_WEBHOOK_MODE,
    BOT_WEBHOOK_PATH,
    BOT_WEBHOOK_PORT,
    TELEGRAM_BOT_TOKEN,
)
from handlers import ai_dialog, filter_search, main_menu, place_actions, start

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def build_dispatcher() -> Dispatcher:
    dp = Dispatcher(storage=MemoryStorage())
    for r in (start.router, main_menu.router, filter_search.router, ai_dialog.router, place_actions.router):
        dp.include_router(r)
    return dp


async def run_webhook(bot: Bot):
    from aiohttp import web

    dp = build_dispatcher()

    async def telegram_webhook(request):
        update = await request.json()
        await dp.feed_update(bot, update)
        return web.Response(status=200)

    app = web.Application()
    app.router.add_post(BOT_WEBHOOK_PATH, telegram_webhook)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, BOT_WEBHOOK_HOST, BOT_WEBHOOK_PORT)
    await site.start()
    webhook_url = f"http://{BOT_WEBHOOK_HOST}:{BOT_WEBHOOK_PORT}{BOT_WEBHOOK_PATH}"
    await bot.set_webhook(webhook_url)
    logger.info("Webhook listening on %s", webhook_url)
    await site.wait_closed()


async def main():
    if not TELEGRAM_BOT_TOKEN or "your_bot_token" in TELEGRAM_BOT_TOKEN:
        logger.error(
            "TELEGRAM_BOT_TOKEN not configured. "
            "Set a real token in .env and restart. Exiting."
        )
        return

    parser = argparse.ArgumentParser()
    parser.add_argument("--polling", action="store_true", help="Run in polling mode (dev)")
    args = parser.parse_args()

    bot = Bot(
        token=TELEGRAM_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    if args.polling or not BOT_WEBHOOK_MODE:
        dp = build_dispatcher()
        logger.info("Bot polling started...")
        await dp.start_polling(bot)
    else:
        await run_webhook(bot)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
