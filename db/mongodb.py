from motor.motor_asyncio import AsyncIOMotorClient
from core.config import MONGO_DETAILS

client = AsyncIOMotorClient(MONGO_DETAILS)
database = client.fastapi_project
user_collection = database.get_collection("users")
