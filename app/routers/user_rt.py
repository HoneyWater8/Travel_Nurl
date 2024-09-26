from fastapi import APIRouter, HTTPException, Request, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.services.user_service import UserService
from app.schemas.user import UserCreate, UserInKakao, UserLogin
from starlette.requests import Request
from starlette.responses import RedirectResponse

router = APIRouter(prefix="/user", tags=["user"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
userService = UserService()


## 로그아웃을 확인하기 위한 메소드
@router.get("/OkLogOut")
async def Oklogout():
    """
    # 로그아웃 확인 api
    """
    return {"message": "Logout Complete"}


@router.post("/login")
async def login(
    request: Request, userIdorEmail: str = Form(...), password: str = Form(...)
):
    """로그인 API (이메일 또는 아이디)"""
    # 아이디 또는 이메일로 사용자 인증
    user_info = await userService.authenticate_user(userIdorEmail, password)
    if not user_info:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # 로그인 성공 시 사용자 정보를 세션에 저장
    request.session["user"] = {
        "id": user_info.id,
        "email": user_info.email,
        "nickname": user_info.nickname,
    }

    # 로그인 성공 시 사용자 정보 반환
    return {"message": "Login successful", "user": user_info}


@router.post("/register")
async def register(userCreate: UserCreate):
    """
    # 사용자 등록 api
    """
    user_info = await userService.register_user(userCreate)
    # 회원 가입 성공 시 사용자 정보 반환
    return {
        "message": "Login successful",
        "user": user_info,
    }  # redirect URL로 구성할 필요가 있음.


# 카카오 로그인을 시작하기 위한 엔드포인트
# 사용자를 카카오 인증 URL로 리다이렉트
@router.get("/auth/kakao")
async def kakao_login(request: Request):
    """
    # 카카오 회원가입 및 로그인 api
    - 이 api를 실행하면 자동으로 kakao login 페이지로 리디렉션 됩니다.
    """
    scope = "profile_nickname,profile_image,account_email"
    authorizationUrl = f"https://kauth.kakao.com/oauth/authorize?client_id={userService.kakao_client_id}&redirect_uri={userService.kakao_redirect_url}&response_type=code&scope={scope}"
    return RedirectResponse(url=authorizationUrl)  # type: ignore


# 카카오 로그인 후 카카오에서 리디렉션될 엔드포인트
# 카카오에서 제공한 인증코드를 사용하여 엑세스 토큰을 요청
@router.get("/auth/kakao/callback")
async def kakao_callback(request: Request, code: str):
    """카카오 로그인 후 사용자 정보 가져오기"""
    token_info = await userService.get_token(code)
    access_token = token_info.get("access_token")

    if not access_token:
        raise HTTPException(status_code=400, detail="Invalid token")

    request.session["access_token"] = access_token
    user_info = await userService.get_user_info_kakao(access_token)

    if user_info is None:
        raise HTTPException(status_code=400, detail="Failed to retrieve user info")

    new_user = UserInKakao(
        id=str(user_info.get("id")),
        nickname=user_info.get("properties", {}).get("nickname"),
        email=user_info.get("kakao_account", {}).get("email"),
        profile_image_url=user_info.get("properties", {}).get("profile_image"),
        thumbnail_image_url=user_info.get("properties", {}).get("thumbnail_image"),
    )

    # 사용자 정보를 세션에 저장
    request.session["user"] = new_user.dict()

    await userService.get_or_create_kakao(new_user)
    return {
        "message": "KAKAO Login successful",
        "user": new_user.dict(),
    }


# 로그아웃 엔드포인트
@router.get("/logout")
async def logout(request: Request):
    """
    # 로그아웃 api
    - kakao 로그아웃 + 서비스 로그아웃 api 입니다.
    """
    await userService.logout()
    request.session.pop("access_token", None)
    request.session.pop("user", None)
    return RedirectResponse(url="/user/OkLogOut")  # logout Url 지정해서 보내기.


# 액세스 토큰을 새로고침하기 위한 엔드포인트
@router.post("/kakao/refresh_token")
async def refresh_token(refresh_token: str = Form(...)):
    """Kakao 토큰 재발급 API"""
    return await userService.refreshAccessToken_kakao(refresh_token)


@router.get("/me")
async def get_current_user(request: Request):
    """현재 로그인한 사용자 정보 반환API"""
    user = request.session.get("user")
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user
