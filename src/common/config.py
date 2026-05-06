from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "ConvA"
    environment: str = "development"
    debug: bool = True
    database_url: str = ""
    openai_api_key: str = ""
    
    class Config:
        env_file = ".env"

settings = Settings()
