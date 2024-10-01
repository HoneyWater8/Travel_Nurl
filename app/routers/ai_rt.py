from fastapi import APIRouter, UploadFile, File, HTTPException, Request
from app.services.ai_service import ImageAIService
import tempfile
import os
from app.services.record_service import RecordService

router = APIRouter(prefix="/ai", tags=["AI"])
image_ai = ImageAIService()
record_service = RecordService()


@router.post("/find-similar-image/")
async def find_similar_image(request: Request, user_image: UploadFile, user_text: str = None, region_ids: str = None, category_ids: str = None, top_N: int = 5):  # type: ignore
    """
    ### 입력 파라미터

    - **user_image**: 업로드 할 이미지
    - **user_text**: 입력 텍스트
    - **region_ids**: 지역 ID
    - **category_ids**: 카테고리 ID
    - **top_N**: 찾아낼 이미지의 수

    ### 지역 ID (region_ids)

    | ID | 지역                     |
    |----|------------------------|
    | 0  | 기타                    |
    | 1  | 서울                    |
    | 2  | 강원특별자치도           |
    | 3  | 인천                    |
    | 4  | 충청북도                |
    | 5  | 대전                    |
    | 6  | 충청남도                |
    | 7  | 대구                    |
    | 8  | 경상북도                |
    | 9  | 광주                    |
    | 10 | 경상남도                |
    | 11 | 부산                    |
    | 12 | 전북특별자치도           |
    | 13 | 울산                    |
    | 14 | 전라남도                |
    | 15 | 세종특별자치시          |
    | 16 | 제주도                  |
    | 17 | 경기도                  |

    ### 카테고리 ID (category_ids)

    | ID | 카테고리               |
    |----|--------------------|
    | 0  | 기타                |
    | 1  | 자연                |
    | 2  | 역사                |
    | 3  | 휴양                |
    | 4  | 체험                |
    | 5  | 산업                |
    | 6  | 건축                |
    """
    user = request.session.get("user", "guest")

    # 사용자 이미지 임시 파일 저장
    try:
        temp_image_path = ""
        if user != "guest":
            temp_image_path = await record_service.save_search_history(
                user.get("id"), user_image
            )

        # with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        #     temp_file.write(await user_image.read())
        #     temp_image_path = temp_file.name

        if temp_image_path:
            # 유사 장소 찾기
            place = await image_ai.find_similar_image(
                user_image_path=temp_image_path,
                user_text=user_text,
                region_id=region_ids,
                category_id=category_ids,
                top_N=top_N,
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # 임시 파일 삭제
        if temp_image_path and os.path.exists(temp_image_path):
            os.remove(temp_image_path)

    return place
