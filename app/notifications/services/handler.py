from ..gateway.producer_server import ProducerServer


class Handler:

    def __init__(self, producer: ProducerServer) -> None:
        self._producer = producer

    async def publish(self, entity)-> None:
        body = await entity.json()
        self._producer.publish(message={'data': body})
