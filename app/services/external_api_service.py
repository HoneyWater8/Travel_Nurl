import httpx
from app.core.config import settings

class ExternalAPIService:
    def __init__(self):
        self.base_url = "http://apis.data.go.kr/B551011/KorService1/locationBasedList1"
   
    async def get_nearby_tourlist(self, latitude: float, longitude: float, contenttype: int, radius: int):
        query = {
            "numOfRows": 100,
            "pageNo": 1,
            "MobileOS": "ETC",
            "MobileApp": "Travel_Nuri",
            "_type": "json",
            "listYN": "Y",
            "arrange": "O",
            "mapX": longitude,
            "mapY": latitude,
            "radius": radius,
            "contentTypeId": contenttype,
            "serviceKey": settings.SERVICE_KEY,
        }
    
        async with httpx.AsyncClient() as client:
            # Request 객체 생성
            request = httpx.Request("GET", self.base_url, params=query)
            print(f"Request URL: {request.url}")  # 생성된 URL 출력
            response = await client.get(self.base_url, params=query)
            response.raise_for_status()  # 응답 상태 코드가 200이 아닐 경우 예외 발생
            return response.json()