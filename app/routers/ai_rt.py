""" from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.ai_service import ImageAIService
import tempfile
import os

router = APIRouter(prefix="/ai", tags=["AI"])
image_ai = ImageAIService()


@router.post("/find-similar-image/")
async def find_similar_image(user_image: UploadFile = File(...), user_text: str = None, region_ids: str = None, category_ids: str = None, top_N: int = 5):  # type: ignore

    data = {"similar_places": []}

    # 사용자 이미지 임시 파일 저장
    try:
        # 파일 이름이 None일 경우 기본 이름 설정
        filename = user_image.filename if user_image.filename else "user_image"
        suffix = os.path.splitext(filename)[1]  # 파일 확장자 추출

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file.write(await user_image.read())
            temp_image_path = temp_file.name

        # 유사 이미지 찾기
        image = await image_ai.find_similar_image(
            user_image_path=temp_image_path,
            user_text=user_text,
            region_ids=region_ids,
            category_ids=category_ids,
            top_N=top_N,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # 임시 파일 삭제
        if temp_image_path and os.path.exists(temp_image_path):
            os.remove(temp_image_path)

    return image
 """
