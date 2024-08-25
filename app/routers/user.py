from fastapi import APIRouter, Response, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2AuthorizationCodeBearer
import httpx
from app.core.config import settings
from app.services.user_service import UserService
from app.schemas.user import UserCreate, User
from bson import ObjectId  ## 새로운 ID 생성

router = APIRouter()
UserService = UserService()


@router.post("/register", response_model=User)
async def register(user_create: UserCreate):
    return await UserService.register_user(user_create)


@router.get("/auth/kakao")
async def kakao_login():
    authorizationUrl = f"https://kauth.kakao.com/oauth/authorize?client_id={settings.KAKAO_CLIENT_ID}&redirect_uri={settings.KAKAO_REDIRECT_URL}&response_type=code&scope=profile_nickname,profile_image,account_email"
    return RedirectResponse(url=authorizationUrl)  # type: ignore


@router.get("/auth/kakao/callback")
async def kakao_callback(code: str, response: Response):
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            "https://kauth.kakao.com/oauth/token",
            params={
                "grant_type": "authorization_code",
                "client_id": settings.KAKAO_CLIENT_ID,
                "client_secret": settings.KAKAO_CLIENT_SECRET,
                "redirect_uri": settings.KAKAO_REDIRECT_URL,
                "code": code,
            },
        )
        token_data = token_response.json()

    access_token = token_data.get("access_token")
    if not access_token:
        raise HTTPException(status_code=400, detail="Invalid token")

    async with httpx.AsyncClient() as client:
        user_response = await client.get(
            "https://kapi.kakao.com/v2/user/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        user_info = user_response.json()
    # 사용자 정보에서 필요한 데이터 추출

    kakao_id = user_info.get("id")
    email = user_info.get("kakao_account", {}).get("email")
    username = user_info.get("properties", {}).get("nickname")
    profile_image_url = user_info.get("properties", {}).get("profile_image")
    thumbnail_image_url = user_info.get("properties", {}).get("thumbnail_image")

    # 사용자 등록 또는 조회
    user_response = await UserService.get_or_create_user(
        kakao_id, username, email, thumbnail_image_url, profile_image_url
    )

    return user_response


@router.post("/auth/logout")
async def logout(response: Response):
    # 로그아웃 처리: 세션 쿠키 삭제
    response.delete_cookie("session")  # 세션 쿠키 삭제
    return {"message": "로그아웃 성공"}
