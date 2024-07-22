from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "lists" DROP CONSTRAINT "fk_lists_users_335db26c";
        ALTER TABLE "lists" DROP CONSTRAINT "fk_lists_anime_473ab335";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "lists" ADD CONSTRAINT "fk_lists_anime_473ab335" FOREIGN KEY ("anime_id") REFERENCES "anime" ("id") ON DELETE CASCADE;
        ALTER TABLE "lists" ADD CONSTRAINT "fk_lists_users_335db26c" FOREIGN KEY ("user_id") REFERENCES "users" ("id") ON DELETE CASCADE;"""
