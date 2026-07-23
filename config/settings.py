from functools import lru_cache
from pydantic import BaseModel, Field
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

class Settings(BaseSettings):
    app_name: str
    debug: bool = False
    mongo : MongoConfig
    redis: RedisConfig
    log: LoggerConfig = Field(default_factory=LoggerConfig)
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__"
    )


@lru_cache
def get_settings():
    return Settings()