from databases import Database

import os


async def get_database() -> Database:
    try:
        database = Database(
            f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
        )

        # database = Database(
        #     f"postgresql://postgres@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
        # )
        await database.connect()
        yield database
    finally:
        await database.disconnect()
