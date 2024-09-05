from typing import Optional
from pydantic import BaseModel, EmailStr, HttpUrl
from datetime import datetime


## 회원 가입할 때 사용.
## 사용 목적 : 데이터의 유효성 검사와 직렬화를 위해서., 주로 요청 본문이나 응답의 형식을 정의할 때 사용.
class User(BaseModel):
    id: str
    nickname: str
    password: Optional[str]
    email: EmailStr


class UserCreate(User):
    hashed_password: str  # 비밀번호는 평문으로 받음
    created_at: datetime  # 생성일자
    updated_at: datetime  # 수정일자


class UserInKakao(User):
    thumbnail_image_url: HttpUrl
    profile_image_url: HttpUrl
