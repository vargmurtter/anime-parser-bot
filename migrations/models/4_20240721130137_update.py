from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "anime" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "anime_id" BIGINT NOT NULL,
    "poster_url" TEXT NOT NULL,
    "poster_thumb_url" TEXT NOT NULL,
    "type" TEXT NOT NULL,
    "rating" TEXT NOT NULL,
    "episodes" INT NOT NULL,
    "aired" TEXT NOT NULL,
    "ended" TEXT NOT NULL,
    "updated_date" TIMESTAMPTZ NOT NULL
);
        DROP TABLE IF EXISTS "articles";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "anime";"""
