from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from the .env file.

    This keeps sensitive values like API keys outside the codebase.
    """

    app_name: str = "NUKHBA AI Interview Agent"
    app_env: str = "development"

    openrouter_api_key: str
    openrouter_model: str = "qwen/qwen-2.5-72b-instruct"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()