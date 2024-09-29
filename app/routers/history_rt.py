from fastapi import APIRouter, File, UploadFile, Request, HTTPException
from fastapi.security import OAuth2PasswordBearer
from app.services.record_service import RecordService
from app.schemas.place import blur_place

router = APIRouter(prefix="/record", tags=["Record"])
record_service = RecordService()


@router.post("/upload")
async def upload_file(file: UploadFile, request: Request):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    await record_service.save_search_history(file=file, user_id=user.get("id"))
    return {"message": f"{file.filename} has been added to favorites."}


@router.post("/favorites")
async def add_favorite(place: blur_place, request: Request):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    place_dict = place.model_dump()
    added = await record_service.add_favorite(user.get("id"), place_dict)

    if not added:
        raise HTTPException(status_code=400, detail="Already added to favorites.")

    return {"message": f"{place.name} has been added to favorites."}


@router.get("/favorites")
async def get_favorites(request: Request):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    favorites = await record_service.get_favorites(user.get("id"))
    return {"favorites": favorites}


@router.delete("/favorites")
async def remove_favorite(place: blur_place, request: Request):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    if await record_service.remove_favorite(user.get("id"), str(place.blur_image)):
        return {"message": f"{place.name} has been removed from favorites."}
    else:
        raise HTTPException(status_code=404, detail="Favorite not found")


@router.get("/history")
async def get_search_history(request: Request):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return await record_service.get_search_history(user.get("id"))
