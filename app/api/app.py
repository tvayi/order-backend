import grpc
import inventory_pb2
import inventory_pb2_grpc
from fastapi import Depends, FastAPI
from pydantic import BaseModel

from .services import get_mongo_service
from .settings import Settings
from ..notifications.enum import EnvironmentVariables
from ..notifications.gateway.producer_server import ProducerServer
from ..notifications.services.handler import Handler

app = FastAPI()


class Order(BaseModel):
    code: str
    created_at: str

    class Config:
        schema_extra = {
            "example": {
                "code": "ORD123",
                "created_at": "2022-01-01"
            }
        }


class ProductItem(BaseModel):
    product_code: str
    name: str
    amount: int
    price: float

    class Config:
        schema_extra = {
            "example": {
                "product_code": "PROD123",
                "name": "Product name",
                "amount": 1,
                "price": 100.50
            }
        }


@app.get("/orders/{order_code}/items", response_model=list[ProductItem])
async def get_order_items_from_mongo(
    order_code: str,
    db=Depends(get_mongo_service)
):
    product_items = await db.get_order_product_items(order_code)
    return product_items


@app.post("/orders", response_model=Order)
async def create_order(order: Order, db=Depends(get_mongo_service)):
    created_order = await db.create_order(order.code, order.created_at)

    producer = ProducerServer(
        queue=EnvironmentVariables.RABBITMQ_QUEUE.get_env(),
        host=EnvironmentVariables.RABBITMQ_HOST.get_env(),
        routing_key=EnvironmentVariables.RABBITMQ_ROUTING_KEY.get_env(),
        username=EnvironmentVariables.RABBITMQ_USERNAME.get_env(),
        password=EnvironmentVariables.RABBITMQ_PASSSWORD.get_env(),
        exchange=EnvironmentVariables.RABBITMQ_EXCHANGE.get_env()
    )
    handler = Handler(producer)
    await handler.publish(order)

    return created_order


@app.post("/orders/{order_code}/items", response_model=ProductItem)
async def add_product_item(
    order_code: str,
    product_item: ProductItem,
    db=Depends(get_mongo_service)
):
    channel = grpc.insecure_channel(Settings.grpc_server_url)
    stub = inventory_pb2_grpc.inventoryServiceStub(channel)

    inventory_request = inventory_pb2.InventoryRequest(
        product_code=product_item.product_code,
    )

    response = stub.GetInventory(inventory_request)

    if response.amount < product_item.amount:
        raise Exception('Insufficient inventory')

    created_item = await db.add_product_item_to_order(
        product_item.product_code,
        order_code,
        product_item.name,
        product_item.amount,
        product_item.price
    )
    return created_item
