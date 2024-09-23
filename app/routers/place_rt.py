from fastapi import APIRouter, HTTPException
from app.services.place_service import PlaceService
from app.schemas.place import ImageInfo

placeService = PlaceService()

router = APIRouter(prefix="/api", tags=["api"])


@router.get("/tourist-images")
async def get_random_image(num: int) -> list[ImageInfo]:
    """
    #### 랜덤으로 숫자를 가져오는 api
    num : 가져오고자 하는 사진의 갯수 입력.
    """
    try:
        items: list[ImageInfo] = await placeService.get_random_images(num)
        if not items:
            raise HTTPException(status_code=404, detail="No images found")
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
