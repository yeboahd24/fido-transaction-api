from app.routers import auth, transactions, analytics
from app.middleware.authentication import AuthenticateUserMiddleware
from databases import Database

from fastapi import FastAPI, Depends
from redis import Redis
import os


app = FastAPI()


redis = Redis(host=os.getenv("REDIS_HOST"), port=int(os.getenv("REDIS_PORT")), db=0)


# async def get_database() -> Database:
#     try:
#         database = Database(
#             f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
#         )
#
#         # database = Database(
#         #     f"postgresql://postgres@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
#         # )
#         await database.connect()
#         yield database
#     finally:
#         await database.disconnect()
#
#
# database = Database(
#     f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
# )
#
# redis = Redis(host=os.getenv("REDIS_HOST"), port=int(os.getenv("REDIS_PORT")), db=0)
#
# # authentication middleware
# app.add_middleware(AuthenticateUserMiddleware, database=database)
#
# app.include_router(
#     auth.router,
#     prefix="/auth",
#     tags=["Authentication"],
#     dependencies=[Depends(get_database)],
# )
# app.include_router(
#     transactions.router,
#     prefix="/transactions",
#     tags=["Transactions"],
#     dependencies=[Depends(get_database)],
# )
# app.include_router(
#     analytics.router,
#     prefix="/analytics",
#     tags=["Analytics"],
#     dependencies=[Depends(get_database)],
# )
#
#
# @app.on_event("startup")
# async def startup():
#     await database.connect()
#     await redis.connection.connect()
#
#
# @app.on_event("shutdown")
# async def shutdown():
#     await database.disconnect()
#
#


redis = None


# Asynchronous database connection function
async def get_database() -> Database:
    try:
        database = Database(
            f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
        )
        await database.connect()
        yield database
    finally:
        await database.disconnect()


database = Database(
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

# Add authentication middleware with database dependency
app.add_middleware(AuthenticateUserMiddleware, database=database)

# Include routes with database dependency
app.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"],
    dependencies=[Depends(get_database)],
)
app.include_router(
    transactions.router,
    prefix="/transactions",
    tags=["Transactions"],
    dependencies=[Depends(get_database)],
)
app.include_router(
    analytics.router,
    prefix="/analytics",
    tags=["Analytics"],
    dependencies=[Depends(get_database)],
)


# Initialize Redis asynchronously in the startup event
# @app.on_event("startup")
# async def startup():
#     global redis
#     await database.connect()
#     await redis
#
#
# @app.on_event("shutdown")
# async def shutdown():
#     await database.disconnect()
#     await redis.close()  # Properly close Redis connection on shutdown
#


@app.on_event("startup")
async def startup():
    await database.connect()
    if redis is not None:
        await redis.connection.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
    if redis is not None:
        await redis.connection.disconnect()
