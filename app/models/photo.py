from pydantic import BaseModel
from datetime import datetime


class PhotoMetadata(BaseModel):
    filename: str
    timestamp: datetime


class SearchHistory(BaseModel):
    user_id: str
    query: str
    timestamp: datetime


class Favorites(BaseModel):
    user_id: str
    filename: str
    timestamp: datetime
