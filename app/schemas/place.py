from pydantic import BaseModel
from typing import List, Optional


## Image 클래스
class ImageBase(BaseModel):
    img_name: Optional[str] = None
    img_url: str


class ImageInfo(ImageBase):  # 랜덤 배너 사진에 사용
    place_name: str


## Place 클래스
class PlaceBase(BaseModel):
    name: str
    address: str


class PlaceCreate(PlaceBase):  # 사용자가 장소를 새로 저장할 때 사용
    pass


class PlaceInfo(PlaceBase):  # 랜덤으로 장소 추천할 때 사용
    description: str
    images: List[ImageBase]


class Place_detail(PlaceBase):
    petsAvailable: Optional[str] = None
    tel: Optional[str] = None
    parking: Optional[str] = None
    x: Optional[float] = None
    y: Optional[float] = None
    images: List[ImageBase]


class blur_place(Place_detail):
    blur_image: Optional[str] = None
