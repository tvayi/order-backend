from api.services.mongo_service import MongoService


async def get_mongo_service() -> MongoService:
    db = MongoService()
    await db.connect_to_database()
    return db
