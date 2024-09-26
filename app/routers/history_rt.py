from fastapi import APIRouter, File, UploadFile,Request,HTTPException
from fastapi.security import OAuth2PasswordBearer
from app.services.record_service import RecordService

router = APIRouter()
history_service = RecordService()


@router.post("/search/")
async def search(query: str, request: Request):
    # 비인증된 사용자도 검색 가능
    user = request.session.get('user', 'guest')  # 사용자 정보가 없으면 guest로 처리
    await history_service.save_search_history(user, query)
    return {"query": query}

@router.post("/upload/")
async def upload_photo(file: UploadFile = File(...), request: Request):
    user = request.session.get('user')
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return await history_service.upload_photo(user, file)

@router.post("/favorites/")
async def add_favorite(filename: str, request: Request):
    user = request.session.get('user')
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    await history_service.add_favorite(user, filename)
    return {"message": f"{filename} has been added to favorites."}

@router.get("/favorites/")
async def get_favorites(request: Request):
    user = request.session.get('user')
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return await history_service.get_favorites(user)

@router.get("/search/history/")
async def get_search_history(request: Request):
    user = request.session.get('user')
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return await history_service.get_search_history(user)