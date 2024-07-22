from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "anime" ALTER COLUMN "episodes" TYPE TEXT USING "episodes"::TEXT;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "anime" ALTER COLUMN "episodes" TYPE INT USING "episodes"::INT;"""
