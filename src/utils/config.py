from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    polygon_rpc_url: str = "https://polygon-rpc.com"
    dune_api_key: str = ""
    goldsky_api_key: str = ""
    
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "polymarket"
    postgres_password: str = "polymarket_secret"
    postgres_db: str = "polymarket_detector"
    
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "password"
    
    target_market: str = ""
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
