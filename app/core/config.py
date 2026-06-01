from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    SECRET_KEY: str 
    ALGORITHM: str 
    ACCESS_TOKEN_EXPIRE_MINUTES: int 
    REFRESH_EXPIRE_DAYS: int 
    HASH_KEY: str 

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
        )

config = Settings()