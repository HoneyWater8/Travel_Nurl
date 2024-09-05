from fastapi import APIRouter, HTTPException
from app.models.place import PlaceItem, PlaceResponse
from app.services.place_service import PlaceService
from app.cosmosdb import get_cosmos_client

placeService = PlaceService(get_cosmos_client())

router = APIRouter()


@router.post("/api/tourist-images")
async def get_random_image():
    try:
        items = await placeService.get_random_images(5)
        if not items:
            raise HTTPException(status_code=404, detail="No images found")
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
