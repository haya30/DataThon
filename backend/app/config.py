from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from the .env file.
    """

    app_name: str = "NUKHBA AI Interview Agent"
    app_env: str = "development"

    # Keep this false while developing to avoid wasting tokens.
    use_llm: bool = False

    openrouter_api_key: str = ""
    openrouter_model: str = "deepseek/deepseek-v4-pro"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()