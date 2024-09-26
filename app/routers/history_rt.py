""" from fastapi import APIRouter, File, UploadFile
from app.services.record_service import RecordService

router = APIRouter()
history_service = RecordService()


@router.post("/search/")
async def search(query: str):
    # 비인증된 사용자도 검색 가능
    await history_service.save_search_history(
        "guest", query
    )  # 'guest'로 검색 기록 저장
    return {"query": query}


@router.post("/favorites/")
async def add_favorite(filename: str, current_user: str = Depends(get_current_user)):
    await history_service.add_favorite(current_user, filename)
    return {"message": f"{filename} has been added to favorites."}


@router.get("/favorites/")
async def get_favorites(current_user: str = Depends(get_current_user)):
    return await history_service.get_favorites(current_user)


@router.get("/search/history/")
async def get_search_history(current_user: str = Depends(get_current_user)):
    return await history_service.get_search_history(current_user)
 """