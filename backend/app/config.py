from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    groq_api_key: str = ""
    tavily_api_key: str = ""
    groq_model: str = "openai/gpt-oss-120b"
    frontend_origins: str = "http://localhost:3000"
    log_level: str = "INFO"
    max_requests_per_minute: int = 20
    langsmith_tracing: bool = False
    langsmith_api_key: str = ""
    langsmith_project: str = "researcher-ai"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origins(self):
        return [x.strip().rstrip("/") for x in self.frontend_origins.split(",") if x.strip()]

settings = Settings()
