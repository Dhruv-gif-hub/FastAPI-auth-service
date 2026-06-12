from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    SECRET_KEY: str 
    ALGORITHM: str 
    ACCESS_TOKEN_EXPIRE_MINUTES: int 
    REFRESH_EXPIRE_DAYS: int 
    HASH_KEY: str 
    Database_url : str = "postgresql+asyncpg://postgres:Haldwani%401@172.29.80.1:5432/Blogs"
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
        )

config_value = Settings()