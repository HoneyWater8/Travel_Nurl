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
        parsed_data = []

        for result in data["results"]["bindings"]:
            entry = {
                "name": result.get("name", {}).get("value", "정보 없음"),
                "address": result.get("address", {}).get("value", "정보 없음"),
                "pets_available": result.get("petsAvailable", {}).get(
                    "value", "정보 없음"
                ),  # 애견 동반 가능 여부
                "telephone": result.get("tel", {}).get("value", "정보 없음"),
                "credit_card": result.get("creditCard", {}).get("value", "정보 없음"),
                "parking": result.get("parking", {}).get("value", "정보 없음"),
                "x": result.get("lat", {}).get("value", "정보 없음"),
                "y": result.get("long", {}).get("value", "정보 없음"),
                "image_url": (
                    result.get("depictions", {}).get("value", "").split(", ")
                    if result.get("depictions")
                    else []
                ),
            }
            parsed_data.append(entry)
        return parsed_data
    except HTTPException as e:
        raise e  # HTTPException을 그대로 전달
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get_random-place")
async def get_random_place():
    """
    #### 랜덤으로 숫자를 가져오는 api
    num : 가져오고자 하는 사진의 갯수 입력.
    """
    try:
        items: list[PlaceInfo] = await search_places()
        if not items:
            raise HTTPException(status_code=404, detail="No images found")
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
