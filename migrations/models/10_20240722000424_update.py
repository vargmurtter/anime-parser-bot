from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "anime" DROP COLUMN "updated_date";
        CREATE TABLE IF NOT EXISTS "lists" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "list" TEXT NOT NULL,
    "anime_id" INT NOT NULL REFERENCES "anime" ("id") ON DELETE CASCADE,
    "user_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "anime" ADD "updated_date" TIMESTAMPTZ NOT NULL;
        DROP TABLE IF EXISTS "lists";"""
