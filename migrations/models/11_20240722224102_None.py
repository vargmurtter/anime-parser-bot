from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "anime" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "anime_id" BIGINT NOT NULL UNIQUE,
    "title" TEXT NOT NULL,
    "poster_url" TEXT,
    "poster_thumb_url" TEXT,
    "type" TEXT NOT NULL,
    "rating" TEXT NOT NULL,
    "episodes" TEXT NOT NULL,
    "aired" TEXT NOT NULL,
    "ended" TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS "lists" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "list" TEXT NOT NULL,
    "user_id" INT NOT NULL,
    "anime_id" INT NOT NULL
);
CREATE TABLE IF NOT EXISTS "users" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "tg_id" BIGINT NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
