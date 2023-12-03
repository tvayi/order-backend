import os

from pydantic import BaseSettings


class Settings(BaseSettings):
    mongo_port: int = os.environ["mongo_port"]
    mongo_conn_str: str = os.environ["mongo_conn_str"]
    grpc_server_url: str = os.environ["grpc_server_url"]


settings = Settings()
