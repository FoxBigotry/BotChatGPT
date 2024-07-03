from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env')
    TG_KEY: str
    MONGO_URI: str
    MONGO_DB_NAME: str
    OPENAI_API_KEY: str | None = None
    PROXY: str
    # MODEL_AI: str

    # Default settings
    PROMPT_TOKEN_PRICE: int = 5  # in usd
    COMPLETION_TOKEN_PRICE: int = 15  # in usd
    DEFAULT_MODEL: str = "gpt-4o-2024-05-13"
    DEFAULT_TEMPERATURE: float = 0.8
    HISTORY_LENGTH: int = 5  # in messages
    AUDIOS_DIR: str = "tmp/audios/"
    USER_IDS: str
    ADMIN_ID: str | None = None


settings = Settings()


__all__ = ["settings"]
