from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
from app.core.config import base_settings
from app.services.place_service import PlaceService

uri = base_settings.DATABASE_URL

# Create a new client and connect to the server
client = AsyncIOMotorClient(uri, server_api=ServerApi("1"))
database = client.Test
db = client["Test"]
user_collection = db["test"]


# Send a ping to confirm a successful connection
async def ping_mongodb():
    """MongoDB에 핑을 보내 연결 상태를 확인하는 함수"""
    try:
        await client.admin.command("ping")
        return True
    except Exception:
        return False
