from fastapi import APIRouter, HTTPException
from app.models.place import PlaceItem, PlaceResponse
from app.services.external_api_service import ExternalAPIService

router = APIRouter(prefix="/api", tags=["Tourapi"])

external_service = ExternalAPIService()


@router.get("/get_nearby_tourlist/")
async def get_nearby_tourlist(
    latitude: float, longitude: float, contenttype: int = 12, radius: int = 1000
):
    """
    #### 좌표를 기반으로 각종 정보를 가져오는 url
    - latitude: x좌표
    - longitude : Y좌표
    - contenttype :  (12:관광지, 14:문화시설, 15:축제공연행사, 25:여행코스, 28:레포츠, 32:숙박, 38:쇼핑, 39:음식점)
    - radius : 거리반경(단위:m) , Max값 20000m=20Km
    """
    try:
        # ExternalAPIService를 통해 데이터 c 가져오기
        data = await external_service.get_nearby_tourlist(
            latitude, longitude, contenttype, radius
        )
        # JSON 데이터에서 필요한 정보 추출
        items = []
        for item in (
            data.get("response", {}).get("body", {}).get("items", {}).get("item", [])
        ):
            tour_item = PlaceItem(
                addr1=item.get("addr1"),
                addr2=item.get("addr2"),
                booktour=item.get("booktour"),
                dist=item.get("dist"),
                firstimage=item.get("firstimage"),
                firstimage2=item.get("firstimage2"),
                mapx=item.get("mapx"),
                mapy=item.get("mapy"),
                tel=item.get("tel"),
                title=item.get("title"),
            )
            items.append(tour_item)

        # 모든 아이템을 추가한 후 PlaceResponse 객체 생성
        tour_response = PlaceResponse(items=items)
        return tour_response  # TourResponse 객체 반환

    except HTTPException as http_err:
        raise http_err  # API 호출에서 발생한 HTTP 예외 처리
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error occurred: {str(e)}")
