# app/config.py
from pydantic_settings import BaseSettings
import yaml


class Settings(BaseSettings):  # type: ignore
    SERVICE_KEY: str
    DEBUG: bool
    DATABASE_URL: str
    KAKAO_CLIENT_ID: str
    KAKAO_CLIENT_SECRET: str
    KAKAO_REDIRECT_URL: str
    DATABASE_URL: str
    COSMOS_KEY: str


def load_config():
    with open("app/config.yml", "r") as stream:
        return yaml.safe_load(stream)


# 설정 로드
settings = Settings(**load_config())
