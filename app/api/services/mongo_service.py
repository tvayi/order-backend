from api.settings import settings
from motor.motor_asyncio import AsyncIOMotorClient


class MongoService:
    def __init__(self):
        self.productItem = None
        self.order = None
        self.db = None
        self.client = None

    async def connect_to_database(self):
        self.client = AsyncIOMotorClient(
            settings.mongo_conn_str,
            maxPoolSize=100,
            minPoolSize=10,
        )
        self.db = self.client.myDB
        self.productItem = self.db.productItem
        self.order = self.db.order

    async def get_order_product_items(self, order_code: str) -> list:
        productItems = await self.db.productItem.find(
            {"order_code": order_code}
        ).to_list(100)
        return productItems

    async def create_order(self, code: str, created_at: str) -> dict:
        order_doc = {"code": code, "created_at": created_at}
        result = await self.order.insert_one(order_doc)
        order_doc["_id"] = result.inserted_id
        return order_doc

    async def add_product_item_to_order(
        self,
        product_code: str,
        order_code: str,
        name: str,
        amount: int,
        price: float
    ) -> dict:
        product_item_doc = {
            "product_code": product_code,
            "order_code": order_code,
            "name": name,
            "amount": amount,
            "price": price,
        }
        result = await self.productItem.insert_one(product_item_doc)
        product_item_doc["_id"] = result.inserted_id
        return product_item_doc
