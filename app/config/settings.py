from functools import lru_cache
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class MongoConfig(BaseModel):
    url : str
    db_name : str

class RedisConfig(BaseModel):
    host : str
    port : int = 6399

class LoggerConfig(BaseModel):
    use_json : bool = False
    level : str = "INFO"
    file: str | None = ".log/app.log"


class JWTConfig(BaseModel):

    secret: str

    refresh_secret: str

    algorithm: str = "HS256"

    access_token_expiry: int = 900      # 15 min

    refresh_token_expiry: int = 604800  # 7 days

    issuer: str = "auth-service"

    audience: str = "mcp-api"

    # @field_validator("secret")
    # @classmethod
    # def validate_secret(cls, value: str):

    #     if(len(value)<256):
    #         raise ValueError("Secret must greater than 256 characters")



class Settings(BaseSettings):
    app_name: str
    debug: bool = False
    base_url: str = "http://localhost:8000"
    mongo : MongoConfig
    redis: RedisConfig
    log: LoggerConfig = Field(default_factory=LoggerConfig)
    jwt: JWTConfig

    # Which product catalog implementation is active: "v1" (original fixture
    # schema) or "v2" (extended catalog schema). Lets callers (MCP tools, etc.)
    # switch without code changes.
    catalog_version: str = "v1"

    # Base URL of the external catalog source used to seed the v2 product
    # collection. Left blank by default — set in .env for the seed script.
    catalog_source_url: str = ""

    @field_validator("catalog_version")
    @classmethod
    def normalize_catalog_version(cls, value: str) -> str:
        return value.strip().lower()

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__"
    )


@lru_cache
def get_settings():
    return Settings()