"""
Application configuration using pydantic-settings
"""
from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./agenthub.db"

    # Volcano Engine (Orchestrator)
    VOLCANO_API_KEY: str = ""
    VOLCANO_MODEL: str = "doubao-pro-32k"
    VOLCANO_ENDPOINT: str = "https://ark.cn-beijing.volces.com/api/v3"

    # OpenAI compatible
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"

    # DeepSeek OpenAI-compatible backend
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    DEEPSEEK_MODEL: str = "deepseek-v4-flash"
    DEEPSEEK_TIMEOUT_SECONDS: float = 60.0
    DEEPSEEK_MAX_TOKENS: int = 2048

    # CLI paths
    OPENCODE_BINARY_PATH: str = "opencode"
    CODEX_BINARY_PATH: str = "codex"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
