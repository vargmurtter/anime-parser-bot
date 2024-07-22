from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "articles" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "habr_id" BIGINT NOT NULL UNIQUE,
    "title" TEXT NOT NULL,
    "description" TEXT NOT NULL,
    "text" TEXT NOT NULL,
    "date" TIMESTAMPTZ NOT NULL,
    "parse_date" TIMESTAMPTZ NOT NULL
);
        ALTER TABLE "users" DROP COLUMN "name";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users" ADD "name" TEXT;
        DROP TABLE IF EXISTS "articles";"""
