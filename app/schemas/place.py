from pydantic import BaseModel
from typing import List, Optional


## Image 클래스
class ImageBase(BaseModel):
    img_name: Optional[str] = None
    img_url: str


class ImageInfo(ImageBase):
    place_name: str


## Place 클래스
class PlaceBase(BaseModel):
    name: str
    images: List[ImageBase]


class PlaceCreate(PlaceBase):
    pass


class PlaceInfo(PlaceBase):
    address: str
    description: str
