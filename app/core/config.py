# app/core/config.py
from dotenv import load_dotenv
import os


class BaseSettings:
    def __init__(self):
        load_dotenv(".env")  # 환경 변수 로딩
        self.SERVICE_KEY: str = self.get_env("SERVICE_KEY")
        self.DEBUG: bool = self.get_env("DEBUG").lower() == "true"
        self.SESSION_KEY: str = self.get_env("SESSION_KEY")
        self.load_env_variables()

    def load_env_variables(self):
        """서브클래스에서 필요한 환경 변수를 정의하도록 합니다."""
        pass

    def get_env(self, key: str) -> str:
        value = os.getenv(key) or os.getenv("APPSETTING_" + key)
        if value is None:
            raise ValueError(f"Environment variable '{key}' not set")
        return value


class KakaoSettings(BaseSettings):
    def load_env_variables(self):
        self.CLIENT_ID = self.get_env("KAKAO_CLIENT_ID")
        self.CLIENT_SECRET = self.get_env("KAKAO_CLIENT_SECRET")
        self.REDIRECT_URL = self.get_env("KAKAO_REDIRECT_URL")
        self.LOGOUT_REDIRECT_URI = self.get_env("KAKAO_LOGOUT_REDIRECT_URI")


class CosmosSettings(BaseSettings):
    def load_env_variables(self):
        self.KEY = self.get_env("COSMOS_KEY")
        self.BLOB_CONNECTION_KEY = self.get_env("COSMOS_BLOB_CONNECTION_KEY")
        self.END_POINT = self.get_env("COSMOS_END_POINT")


class MongoSettings(BaseSettings):
    def load_env_variables(self):
        self.DB_URL = self.get_env("DATABASE_URL")
        self.DB = self.get_env("DATABASE")
        self.USER_COLLECTION = self.get_env("USER_COLLECTION")


class PineconeSettings(BaseSettings):
    def load_env_variables(self):
        self.key = self.get_env("PINECONE_KEY")
        self.environment = "us-east-1"
        self.index_name = "travelnuri"


# 설정 인스턴스 생성
pinecone_settins = PineconeSettings()
cosmos_settings = CosmosSettings()
kakao_settings = KakaoSettings()
mongo_settings = MongoSettings()
base_settings = BaseSettings()
