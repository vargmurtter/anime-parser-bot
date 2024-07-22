import os
import asyncio
import logging
import config
from tortoise import Tortoise
from app.handlers import start, anime_info, anime_search, anime_lists
from loaders import bot, dp


async def run():
    await Tortoise.init(config=config.TORTOISE_SETTINGS)
    await Tortoise.generate_schemas()

    if not os.path.exists("logs/"):
        os.makedirs("logs/")

    logging_mode = logging.DEBUG if config.DEBUG_MODE else logging.INFO
    logging.basicConfig(
        format="%(asctime)s %(levelname)s => %(message)s",
        level=logging_mode,
        datefmt="[%Y-%m-%d %H:%M:%S]",
        handlers=[
            logging.FileHandler("logs/bot.txt"),
            logging.StreamHandler(),
        ],
    )

    logging.info(f"DEBUG_MODE: {config.DEBUG_MODE}")
    logging.info(f"BOT_ALIVE: {config.BOT_ALIVE}")

    dp.include_routers(
        start.router, anime_info.router, anime_search.router, anime_lists.router
    )

    await bot.delete_webhook(drop_pending_updates=False)
    await dp.start_polling(bot)

    await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(run())
