from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "CareerCrawler API"
    version: str = "1.0.0"
    database_url: str = "sqlite:///./careercrawler.db"
    cors_origins: list[str] = ["*"]
    crawl_delay_min: float = 0.8
    crawl_delay_max: float = 2.2

settings = Settings()
