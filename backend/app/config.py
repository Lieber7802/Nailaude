"""
Application configuration using pydantic-settings
"""
from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./agenthub.db"

    # OpenAI compatible
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"

    # DeepSeek OpenAI-compatible backend
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    DEEPSEEK_MODEL: str = "deepseek-v4-flash"
    DEEPSEEK_TIMEOUT_SECONDS: float = 60.0
    DEEPSEEK_MAX_TOKENS: int = 2048
    OPENCODE_MODEL: str = "deepseek/deepseek-v4-flash"

    # CLI paths
    OPENCODE_BINARY_PATH: str = "opencode"
    CODEX_BINARY_PATH: str = "codex"
    CLI_TIMEOUT_SECONDS: float = 600.0
    CLI_MAX_CONCURRENCY: int = 4

    # Schema creation is convenient for disposable local/test environments only.
    AUTO_CREATE_SCHEMA: bool = False

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
