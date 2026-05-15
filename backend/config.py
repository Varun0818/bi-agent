from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    groq_api_key: str = ""
    database_url: str = "sqlite:///./app.db"
    demo_db_url: str = "sqlite:///./db/demo_data/demo.db"
    chroma_path: str = "./chroma_store"
    max_retries: int = 3
    llm_model: str = "llama-3.3-70b-versatile"
    app_env: str = "development"


settings = Settings()