from pydantic import BaseModel, EmailStr, FileUrl
from datetime import datetime
from bson import ObjectId


class UserBase(BaseModel):
    id: str  # ObjectId를 문자열로 변환하여 저장
    kakaoid: str  # 카카오 아이디가 있을 경우 추가.
    username: str
    email: EmailStr
    thumbnail_image_url: FileUrl
    profile_image_url: FileUrl
    created_at: datetime  # 생성일자
    updated_at: datetime  # 수정일자


class UserCreate(UserBase):
    password: str  # 비밀번호는 평문으로 받음

    class Config:
        # MongoDB ObjectId를 JSON 직렬화 가능하게 설정
        json_encoders = {ObjectId: str}


class User(UserBase):
    class Config:
        from_attributes = True  # ORM 모델과 호환성 설정
