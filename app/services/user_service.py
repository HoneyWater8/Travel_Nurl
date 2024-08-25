from passlib.context import CryptContext
from app.database import user_collection
from datetime import datetime
from app.schemas.user import User, UserCreate
from bson import ObjectId
from fastapi import HTTPException
from pydantic import BaseModel, EmailStr, HttpUrl


class UserService:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    async def register_user(self, user_create: UserCreate) -> User:
        # 이메일 중복 체크
        existing_user = await user_collection.find_one({"email": user_create.email})
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        # 비밀번호 해시
        hashed_password = self.pwd_context.hash(user_create.password)

        # 사용자 데이터 생성
        user_data = {
            "id": str(ObjectId()),  # 새로운 ObjectId 생성
            "username": user_create.username,
            "email": user_create.email,
            "hashed_password": hashed_password,
            "thumbnail_image_url": user_create.thumbnail_image_url,
            "profile_image_url": user_create.profile_image_url,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        # 사용자 저장
        try:
            result = await user_collection.insert_one(user_data)
            user_data["id"] = str(result.inserted_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

        return User(**user_data)

    async def get_or_create_user(
        self,
        kakao_id: str,
        username: str,
        email: str,
        thumbnail_image_url: HttpUrl,
        profile_image_url: HttpUrl,
    ):
        # 카카오 ID로 사용자 조회
        user = await user_collection.find_one({"kakao_id": kakao_id})

        if user is None:
            # 신규 사용자 등록
            new_user = UserCreate(
                id=str(ObjectId()),  # 새로운 ObjectId 생성
                kakaoid= kakao_id,
                username=username,
                email=email,
                thumbnail_image_url=thumbnail_image_url,
                profile_image_url=profile_image_url,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                password=""  # 비밀번호는 필요 없으므로 빈 문자열로 설정
            )

            user_dict = new_user.dict()  # Pydantic 모델을 딕셔너리로 변환
            user_dict["kakao_id"] = kakao_id  # kakao_id 추가
            try:
                result = await user_collection.insert_one(
                    user_dict
                )  # MongoDB에 사용자 데이터 저장
                user_dict["_id"] = str(result.inserted_id)  # 새로 생성된 사용자 ID 추가
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
            return {"message": "회원가입 성공", "user_data": new_user}
        else:
            return {"message": "로그인 성공", "user_data": user}
