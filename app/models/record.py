from datetime import datetime
from app.models.place import ImageBase, blur_place


class SearchHistory(ImageBase):
    user_id: str
    timestamp: datetime


class Favorites(blur_place):
    user_id: str
    timestamp: datetime
