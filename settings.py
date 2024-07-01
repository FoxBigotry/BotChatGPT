from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env')
    TG_KEY: str
    MONGO_URI: str
    MONGO_DB_NAME: str
    OPENAI_API_KEY: str | None = None
    PROXY: str
    MODEL_AI: str


settings = Settings()


__all__ = ["settings"]
