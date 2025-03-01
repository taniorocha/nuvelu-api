from fastapi import FastAPI
from pymongo import AsyncMongoClient

async def startup_db_client(app: FastAPI):
    mongodb_client = AsyncMongoClient(app.settings.mongo_db_str_connection)
    nuvelu_db = mongodb_client["nuveludb"]

    app.mongodb_client = mongodb_client
    app.db = nuvelu_db

    print("MongoDB connected.")

async def shutdown_db_client(app):
    app.mongodb_client.close()
    print("Database disconnected.")