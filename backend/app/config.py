from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_ENV: str = "dev"

    JWT_SECRET: str = "supersecret"
    JWT_ALG: str = "HS256"

settings = Settings()
