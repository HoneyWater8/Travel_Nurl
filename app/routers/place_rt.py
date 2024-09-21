from fastapi import APIRouter, HTTPException
from app.models.place import PlaceItem, PlaceResponse
from app.services.place_service import PlaceService
from app.cosmosdb import get_cosmos_client

placeService = PlaceService()

router = APIRouter(prefix="/api", tags=["api"])


@router.get("/tourist-images")
async def get_random_image(num: int):
    """
    #### 랜덤으로 숫자를 가져오는 api
    num : 가져오고자 하는 사진의 갯수 입력.
    """
    try:
        items = await placeService.get_random_images(num)
        if not items:
            raise HTTPException(status_code=404, detail="No images found")
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
