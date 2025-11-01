from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_ENV: str = "dev"

    DB_USER: str = "postgres"
    DB_PASS: str = "postgres"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "crisis-connect"

    @property
    def DB_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    JWT_SECRET: str = "supersecret"
    JWT_ALG: str = "HS256"

settings = Settings()
