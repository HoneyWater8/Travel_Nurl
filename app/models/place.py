from typing import List, Optional
from pydantic import BaseModel


## Image 클래스
class ImageBase(BaseModel):
    img_name: Optional[str] = None
    img_url: str


## Place 클래스
class PlaceBase(BaseModel):
    name: str
    address: str


class PlaceCreate(PlaceBase):  # 사용자가 장소를 새로 저장할 때 사용
    pass


class Place_detail(PlaceBase):
    petsAvailable: Optional[str] = None
    tel: Optional[str] = None
    parking: Optional[str] = None
    x: Optional[float] = None
    y: Optional[float] = None
    images: List[ImageBase]


class PlaceItem(BaseModel):
    addr1: Optional[str]  ## 주소
    addr2: Optional[str]  ## 상세 주소
    dist: Optional[float]  ## 해당 지역으로부터의 거리
    firstimage: Optional[str]
    firstimage2: Optional[str]
    booktour: Optional[
        str
    ]  ## 교과서 속 여행지 여부/ 있을 시 : "0"/ 없을 시 : "아무 것도 없음."
    mapx: float  ## GPS X 좌표
    mapy: float  ## GPS Y 좌표
    tel: Optional[str]  # 전화번호는 선택적일 수 있음
    title: str  ## 제목


class blur_place(Place_detail):
    blur_image: Optional[str] = None


class PlaceResponse(BaseModel):
    items: List[PlaceItem]
