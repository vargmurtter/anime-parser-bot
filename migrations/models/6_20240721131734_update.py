from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE UNIQUE INDEX "uid_anime_anime_i_89fcca" ON "anime" ("anime_id");
        CREATE UNIQUE INDEX "uid_users_tg_id_826a93" ON "users" ("tg_id");"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP INDEX "idx_anime_anime_i_89fcca";
        DROP INDEX "idx_users_tg_id_826a93";"""
