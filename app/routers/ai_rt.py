""" from fastapi import APIRouter, UploadFile, File
from fastapi.responses import HTMLResponse
from app.services.place_service import PlaceService

router = APIRouter()


@router.post("/find-similar-image/")
async def find_similar_image(user_image: UploadFile = File(...), user_text: str = None):  # type: ignore

    data = {"similar_places": []}

    # 사용자 이미지 저장
    user_image_path = f"temp_{user_image.filename}"
    with open(user_image_path, "wb") as f:
        f.write(await user_image.read())

    image, top_N_scores = PlaceService.find_similar_image(
        user_image_path, user_text, top_N=5
    )

    # 결과 HTML 반환
    for id, score in zip(image, top_N_scores):
        data["similar_places"].append(
            {
                "image": image[id],
                "score": score,
            }
        )

    return data
 """
