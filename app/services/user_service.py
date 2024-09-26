from passlib.context import CryptContext
from app.database import database
from datetime import datetime
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.schemas.user import UserCreate, UserInKakao, User
from app.models.user import UserInDB, KakaoUserInDB
from fastapi import HTTPException
from datetime import datetime
import httpx
from app.core.config import kakao_settings, mongo_settings
from app.database import database


class UserService:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.db = database
        self.collection = self.db[mongo_settings.USER_COLLECTION]
        self.kakao_client_id = kakao_settings.CLIENT_ID
        self.kakao_client_secret = kakao_settings.CLIENT_SECRET
        self.kakao_redirect_url = kakao_settings.REDIRECT_URL

    async def authenticate_user(self, identifier: str, password: str):
        try:
            # 이메일 또는 아이디로 사용자 검색
            user = await self.find_user_by_identifier(identifier)
            if user is None:
                raise ValueError("사용자를 찾을 수 없습니다.")

            if not self.verify_password(password, user["hashed_password"]):
                raise ValueError("비밀번호가 일치하지 않습니다.")

            user_info = User(
                email=user["email"], id=user["id"], nickname=user["nickname"]
            )
            return user_info

        except ValueError as ve:
            print(f"Authentication error: {ve}")
            return None
        except Exception as e:
            print(f"Unexpected error during authentication: {e}")
            return None

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        # bcrypt를 사용하여 비밀번호 비교
        return self.pwd_context.verify(plain_password, hashed_password)

    def hash_password(self, plain_password: str) -> str:
        # 비밀번호 해싱
        return self.pwd_context.hash(plain_password)

    async def find_user_by_identifier(self, identifier: str):
        # 이메일 또는 아이디로 사용자 조회하는 로직
        # 예: 데이터베이스에서 사용자 검색하는 코드
        user = await self.get_user_by_email(identifier) or await self.get_user_by_id(
            identifier
        )
        if user is None:
            raise ValueError("사용자를 찾을 수 없습니다.")
        return user

    async def get_user_by_email(self, email: str):
        # 이메일로 사용자 검색하는 로직
        return await self.collection.find_one({"email": email})

    async def get_user_by_id(self, user_id: str):
        # 아이디로 사용자 검색하는 로직
        return await self.collection.find_one({"id": user_id})

    async def register_user(self, user: UserCreate) -> User:
        await self._check_existing_user(user.id, user.email)
        hashed_password = self.hash_password(user.password)  # type: ignore

        user_data = UserInDB(
            id=user.id,
            nickname=user.nickname,
            email=user.email,
            hashed_password=hashed_password,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        user_info = User(id=user.id, nickname=user.nickname, email=user.email)
        await self._save_user(user_data)
        return user_info

    async def get_or_create_kakao(self, user: UserInKakao) -> UserInKakao:
        # 아이디 중복 체크 로직 추가
        existing_user = await self.collection.find_one({"id": user.id})
        if existing_user:
            return user
        else:
            user_data = KakaoUserInDB(
                id=user.id,
                nickname=user.nickname,
                email=user.email,
                thumbnail_image_url=str(user.thumbnail_image_url),
                profile_image_url=str(user.profile_image_url),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            await self._save_user(user_data)
            return user

    async def _check_existing_user(self, user_id, email):
        if await self.collection.find_one({"id": user_id}):
            raise HTTPException(status_code=400, detail="Id already registered")
        if await self.collection.find_one({"email": email}):
            raise HTTPException(status_code=400, detail="Email already registered")

    async def _save_user(self, user_data):
        try:
            await self.collection.insert_one(user_data.model_dump())
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def get_user_info_kakao(self, access_token):
        async with httpx.AsyncClient() as client:
            user_response = await client.get(
                "https://kapi.kakao.com/v2/user/me",
                headers={"Authorization": f"Bearer {access_token}"},
            )
        return user_response.json() if user_response.status_code == 200 else None

    async def logout(self):
        logout_url = f"https://kauth.kakao.com/oauth/logout?client_id={self.kakao_client_id}&logout_redirect_uri={self.kakao_redirect_url}"
        async with httpx.AsyncClient() as client:
            await client.get(logout_url)

    async def get_token(self, code):
        token_request_url = "https://kauth.kakao.com/oauth/token"
        token_request_payload = {
            "grant_type": "authorization_code",
            "client_id": self.kakao_client_id,
            "redirect_uri": self.kakao_redirect_url,
            "code": code,
            "client_secret": self.kakao_client_secret,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(token_request_url, data=token_request_payload)
        return response.json()

    async def refreshAccessToken_kakao(self, refresh_token):
        url = "https://kauth.kakao.com/oauth/token"
        payload = {
            "grant_type": "refresh_token",
            "client_id": self.kakao_client_id,
            "refresh_token": refresh_token,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=payload)
        return response.json()
