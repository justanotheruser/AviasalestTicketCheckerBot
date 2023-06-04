import asyncio

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine


async def main():
    username = "air_bot_test_user"
    password = "air_bot_test_pass"
    host = "localhost"
    dbname = "air_bot_test"
    engine = create_async_engine(
        f"mysql+asyncmy://{username}:{password}@{host}/{dbname}",
        echo=True,
        pool_pre_ping=True,
    )
    print(engine)
    async with engine.begin() as conn:
        await conn.execute(text("SELECT * FROM flight_direction"))


if __name__ == "__main__":
    asyncio.run(main())
