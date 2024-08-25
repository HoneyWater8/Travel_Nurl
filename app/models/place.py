from typing import List, Optional
from pydantic import BaseModel

class PlaceItem(BaseModel):
    addr1: Optional[str] ## 주소
    addr2 : Optional[str] ## 상세 주소
    dist : Optional[float] ## 해당 지역으로부터의 거리
    firstimage: Optional[str]
    firstimage2 : Optional[str]
    booktour : Optional[str] ## 교과서 속 여행지 여부/ 있을 시 : "0"/ 없을 시 : "아무 것도 없음."
    mapx: float ## GPS X 좌표
    mapy: float ## GPS Y 좌표
    tel: Optional[str]  # 전화번호는 선택적일 수 있음
    title : str ## 제목
class PlaceResponse(BaseModel):
    items: List[PlaceItem]