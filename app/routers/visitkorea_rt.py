from fastapi import APIRouter, HTTPException
from app.services.data_visitkorea import search_place, search_places
from app.schemas.place import PlaceInfo

router = APIRouter(prefix="/api", tags=["Tourapi"])


@router.get("/get_detail_place")
async def get_detail_place(place_name: str):
    """
    # Tourapi 데이터 베이스로부터 지역 정보를 가져오는 api
    - place_name: 찾으려고 하는 장소의 이름.
    """

    try:
        data = await search_place(place_name)
        # 결과 파싱 및 JSON 형태로 변환

        return data
    except HTTPException as e:
        raise e  # HTTPException을 그대로 전달
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get_random-place")
async def get_random_place():
    """
    #### 랜덤으로 장소를 추천해주는 api
    """
    try:
        items: list[PlaceInfo] = await search_places()
        if not items:
            raise HTTPException(status_code=404, detail="No images found")
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
