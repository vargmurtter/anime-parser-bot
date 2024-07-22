import os
from dotenv import load_dotenv

from app.enums import ListType


load_dotenv(override=True)


# Bot config
BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_LINK = os.getenv("BOT_LINK")

BOT_ALIVE = os.getenv("BOT_ALIVE")
BOT_ALIVE = True if BOT_ALIVE == "1" else False

DEBUG_MODE = os.getenv("DEBUG_MODE")
DEBUG_MODE = True if DEBUG_MODE == "1" else False

WEB_APP_URL = os.getenv("WEB_APP_URL")

# redis config
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_DB = os.getenv("REDIS_DB")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_PREFIX = os.getenv("REDIS_PREFIX")

# postgres config
POSTGRES_URL = os.getenv("POSTGRES_URL")
TORTOISE_SETTINGS = {
    "connections": {"default": POSTGRES_URL},
    "apps": {
        "models": {
            "models": ["app.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}


LIST_TYPES = {
    ListType.WATCHING: "Смотрю",
    ListType.PLAN_TO_WATCH: "В планах",
    ListType.COMPLETED: "Просмотрено",
    ListType.DROPPED: "Брошено",
}
