from pydantic import Field

from pydantic_settings import BaseSettings, SettingsConfigDict
class Config(BaseSettings):
    SECRET_KEY: str = Field(..., min_length=6)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60, gt=0, le=1440)
    REFRESH_EXPIRE_DAYS: int = Field(default=5, gt=0, le=12)
    HASH_KEY: str = Field(..., min_length=4)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
        )

config = Config()