# app/core/config.py
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path="config.env")


class BaseSettings:
    def __init__(self):
        self.SERVICE_KEY: str = self.get_env("SERVICE_KEY")
        self.DEBUG: bool = self.get_env("DEBUG").lower() == "true"
        self.DATABASE_URL: str = self.get_env("DATABASE_URL")
        self.SESSION_KEY: str = self.get_env("SESSION_KEY")

    def get_env(self, key: str) -> str:
        value = os.getenv(key)
        if value is None:
            raise ValueError(f"Environment variable '{key}' not set")
        return value


class KakaoSettings(BaseSettings):
    def __init__(self):
        super().__init__()  # 부모 클래스의 초기화 메서드 호출
        self.KAKAO_CLIENT_ID: str = self.get_env("KAKAO_CLIENT_ID")
        self.KAKAO_CLIENT_SECRET: str = self.get_env("KAKAO_CLIENT_SECRET")
        self.KAKAO_REDIRECT_URL: str = self.get_env("KAKAO_REDIRECT_URL")
        self.KAKAO_LOGOUT_REDIRECT_URI: str = self.get_env("KAKAO_LOGOUT_REDIRECT_URI")


class CosmosSettings(BaseSettings):
    def __init__(self):
        super().__init__()
        self.COSMOS_KEY: str = self.get_env("COSMOS_KEY")
        self.COSMOS_BLOB_CONNECTION_KEY: str = self.get_env(
            "COSMOS_BLOB_CONNECTION_KEY"
        )
        self.COSMOS_END_POINT: str = self.get_env("COSMOS_END_POINT")


# 설정 인스턴스 생성
cosmos_settings = CosmosSettings()
kakao_settings = KakaoSettings()
base_settings = BaseSettings()
