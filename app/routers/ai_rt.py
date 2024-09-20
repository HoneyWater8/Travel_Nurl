from fastapi import APIRouter, UploadFile, File
from fastapi.responses import HTMLResponse
from app.services.ai_service import ImageAIService

router = APIRouter(prefix="/ai", tags=["AI"])
image_ai = ImageAIService()


@router.post("/find-similar-image/")
async def find_similar_image(user_image: UploadFile = File(...), user_text: str = None, region_ids: str = None, category_ids: str = None, top_N: int = 5):  # type: ignore

    data = {"similar_places": []}

    # 사용자 이미지 저장
    user_image_path = f"temp_{user_image.filename}"
    with open(user_image_path, "wb") as f:
        f.write(await user_image.read())

    image = image_ai.find_similar_image(
        user_image_path=user_image_path,
        user_text=user_text,
        region_ids=region_ids,
        category_ids=category_ids,
        top_N=top_N,
    )

    return image
