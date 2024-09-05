from passlib.context import CryptContext
from app.database import database
from datetime import datetime
from app.schemas.user import User, UserInKakao
from app.models.user import UserInDB, KakaoUserInDB
from fastapi import HTTPException
from datetime import datetime
import httpx
from app.core.config import settings


class UserService:
    def __init__(self, db=database):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.db = db

    # 사용자 등록 메소드
    async def register_user(self, user: User) -> UserInDB:
        # 아이디 중복 체크 로직 추가
        existing_user = await self.db.test.find_one({"id": user.id})
        if existing_user:
            raise HTTPException(status_code=400, detail="Id already registered")
        # 이메일 중복 체크
        existing_user = await self.db.test.find_one({"email": user.email})
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        # 비밀번호 해시
        hashed_password = self.pwd_context.hash(user.password)  # type: ignore

        # 사용자 데이터 생성
        user_data = UserInDB(
            id=user.id,
            nickname=user.nickname,
            email=user.email,
            hashed_password=hashed_password,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        # 사용자 저장
        try:
            result = await self.db.test.insert_one(user_data.model_dump())
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

        return {"message": "User registered successfully", "user": user_data}  # type: ignore // 해당 부분 나중에 수정하기.

    # 카카오 로그인&회원가입 메서드
    async def get_or_create_kakao(self, user: UserInKakao):
        # 아이디 중복 체크 로직 추가
        existing_user = await self.db.test.find_one({"id": user.id})
        if existing_user:
            return {"message": "User login successfully", "user": user}  # type: ignore // 해당 부분 나중에 수정하기.
        else:
            # 사용자 데이터 생성
            user_data = KakaoUserInDB(
                id=user.id,
                nickname=user.nickname,
                email=user.email,
                thumbnail_image_url=str(user.thumbnail_image_url),
                profile_image_url=str(user.profile_image_url),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            try:
                result = await self.db.test.insert_one(user_data.model_dump())
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

            return {"message": "User registered successfully", "user": user_data}  # type: ignore // 해당 부분 나중에 수정하기.

    # 사용자 정보를 가져오는 메서드
    async def get_user_info_kakao(self, access_token):
        async with httpx.AsyncClient() as client:
            user_response = await client.get(
                "https://kapi.kakao.com/v2/user/me",
                headers={"Authorization": f"Bearer {access_token}"},
            )
        return user_response.json() if user_response.status_code == 200 else None

    async def logout(self):
        # 카카오 로그아웃 URL을 호출하여 로그아웃 처리
        logout_url = f"https://kauth.kakao.com/oauth/logout?client_id={settings.KAKAO_CLIENT_ID}&logout_redirect_uri={settings.KAKAO_LOGOUT_REDIRECT_URI}"
        async with httpx.AsyncClient() as client:
            await client.get(logout_url)

    async def get_token(self, code):
        # 카카오로부터 인증 코드를 사용해 액세스 토큰 요청
        token_request_url = "https://kauth.kakao.com/oauth/token"
        token_request_payload = {
            "grant_type": "authorization_code",
            "client_id": settings.KAKAO_CLIENT_ID,
            "redirect_uri": settings.KAKAO_REDIRECT_URL,
            "code": code,
            "client_secret": settings.KAKAO_CLIENT_SECRET,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(token_request_url, data=token_request_payload)
        result = response.json()
        return result

    async def refreshAccessToken_kakao(self, refresh_token):
        # 리프레시 토큰을 사용하여 액세스 토큰 갱신 요청
        url = "https://kauth.kakao.com/oauth/token"
        payload = {
            "grant_type": "refresh_token",
            "client_id": settings.KAKAO_CLIENT_ID,
            "refresh_token": refresh_token,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=payload)
        refreshToken = response.json()
        return refreshToken
