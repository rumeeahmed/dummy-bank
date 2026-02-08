import logging
from typing import Any

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL

from dummy_bank.lib.geolocation_client import GoogleMapsClient


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    def __init__(self, **values: Any) -> None:
        super().__init__(**values)

    API_PORT: int = 8080
    API_HOST: str = "0.0.0.0"
    API_TIMEOUT: int = 120

    LOG_LEVEL: str = "INFO"
    LOG_LEVEL_AS_INT: int = logging.INFO

    DB_HOST: str
    DB_USER: str
    DB_PASS: str
    DB_NAME: str
    DB_PORT: int

    GOOGLE_API_KEY: str
    GOOGLE_API_URL: str

    __cached_google_maps_client: GoogleMapsClient | None = None

    def database_url(self) -> URL:
        return URL.create(
            "postgresql+asyncpg",
            username=self.DB_USER,
            password=self.DB_PASS,
            host=self.DB_HOST,
            port=self.DB_PORT,
            database=self.DB_NAME,
        )

    def google_maps_client(self) -> GoogleMapsClient:
        if not self.__cached_google_maps_client:
            self.__cached_google_maps_client = GoogleMapsClient(
                self.GOOGLE_API_URL, self.GOOGLE_API_KEY
            )
        return self.__cached_google_maps_client
