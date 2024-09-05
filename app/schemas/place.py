from pydantic import BaseModel
from typing import List, Optional


## Image 클래스
class ImageBase(BaseModel):
    img_name: str
    img_url: str


class ImageInfo(ImageBase):
    place_name: str


## Place 클래스
class PlaceBase(BaseModel):
    name: str
    images: List[ImageBase]


class PlaceCreate(PlaceBase):
    pass


class Place(PlaceBase):
    description: Optional[str] = None
