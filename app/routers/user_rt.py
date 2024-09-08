from fastapi import APIRouter, HTTPException, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2AuthorizationCodeBearer
from app.services.user_service import UserService
from app.schemas.user import User, UserInKakao

router = APIRouter()
userService = UserService()


## 로그아웃을 확인하기 위한 메소드
@router.get("/OkLogOut")
async def Oklogout():
    return {"message": "Logout Complete"}


@router.post("/register")
async def register(user: User):
    return await userService.register_user(user)


# 카카오 로그인을 시작하기 위한 엔드포인트
# 사용자를 카카오 인증 URL로 리다이렉트
@router.get("/auth/kakao")
async def kakao_login(request: Request):
    scope = "profile_nickname,profile_image,account_email"
    authorizationUrl = f"https://kauth.kakao.com/oauth/authorize?client_id={userService.kakao_client_id}&redirect_uri={userService.kakao_redirect_url}&response_type=code&scope={scope}"
    return RedirectResponse(url=authorizationUrl)  # type: ignore


# 카카오 로그인 후 카카오에서 리디렉션될 엔드포인트
# 카카오에서 제공한 인증코드를 사용하여 엑세스 토큰을 요청
@router.get("/auth/kakao/callback")
async def kakao_callback(request: Request, code: str):
    token_info = await userService.get_token(code)
    if "access_token" in token_info:
        request.session["access_token"] = token_info["access_token"]
    else:
        raise HTTPException(status_code=400, detail="Invalid token")

    user_info = await userService.get_user_info_kakao(
        request.session.get("access_token")
    )
    if user_info is None:
        raise HTTPException(status_code=400, detail="Failed to retrieve user info")

    # 사용자 정보에서 필요한 데이터 추출
    new_user = UserInKakao(
        id=str(user_info.get("id")),
        nickname=user_info.get("properties", {}).get("nickname"),
        password=None,
        email=user_info.get("kakao_account", {}).get("email"),
        profile_image_url=user_info.get("properties", {}).get("profile_image"),
        thumbnail_image_url=user_info.get("properties", {}).get("thumbnail_image"),
    )
    # 사용자 등록 또는 조회
    response = await userService.get_or_create_kakao(new_user)

    return response


# 로그아웃 엔드포인트
@router.get("/logout")
async def logout(request: Request):
    await userService.logout()
    request.session.pop("access_token", None)
    return RedirectResponse(url="/OkLogOut")


# 액세스 토큰을 새로고침하기 위한 엔드포인트
@router.post("/refresh_token")
async def refresh_token(refresh_token: str = Form(...)):
    new_token_info = await userService.refreshAccessToken_kakao(refresh_token)
    return new_token_info
