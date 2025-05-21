from motor.motor_asyncio import AsyncIOMotorClient
from bson.objectid import ObjectId
from typing import Any, Dict

class DB:
    def __init__(self, db_url: str, db_name: str):
        self.client = AsyncIOMotorClient(db_url)
        self.db = self.client[db_name]

    async def create(self, collection: str, document: Dict[str, Any]) -> str:
        result = await self.db[collection].insert_one(document)
        return str(result.inserted_id)

    async def read(self, collection: str, document_id: str) -> Dict[str, Any]:
        document = await self.db[collection].find_one({"_id": ObjectId(document_id)})
        if document:
            document["_id"] = str(document["_id"])
        return document

    async def update(self, collection: str, document_id: str, update_data: Dict[str, Any]) -> int:
        result = await self.db[collection].update_one({"_id": ObjectId(document_id)}, {"$set": update_data})
        return result.modified_count

    async def delete(self, collection: str, document_id: str) -> int:
        result = await self.db[collection].delete_one({"_id": ObjectId(document_id)})
        return result.deleted_count

    async def find(self, collection: str, query: Dict[str, Any]) -> list:
        cursor = self.db[collection].find(query)
        documents = []
        async for document in cursor:
            document["_id"] = str(document["_id"])
            documents.append(document)
        return documents
