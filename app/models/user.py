from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserBase(BaseModel):
    id: str
    nickname: str
    email: EmailStr

    class Config:
        from_attributes = True


class UserInDB(UserBase):
    hashed_password: str  # 비밀번호는 평문으로 받음
    created_at: datetime  # 생성일자
    updated_at: datetime  # 수정일자


# kakao id 는 id로써 활용한다.
class KakaoUserInDB(UserBase):
    created_at: datetime  # 생성일자
    updated_at: datetime  # 수정일자
    thumbnail_image_url: str
    profile_image_url: str
