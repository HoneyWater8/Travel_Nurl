from typing import Optional
from pydantic import BaseModel, EmailStr, HttpUrl


## 회원 가입할 때 사용.
## 사용 목적 : 데이터의 유효성 검사와 직렬화를 위해서., 주로 요청 본문이나 응답의 형식을 정의할 때 사용.
class User(BaseModel):
    id: str
    nickname: str
    email: EmailStr


# UserLogin 스키마
class UserLogin(BaseModel):
    identifier: str  # 이메일 또는 아이디
    password: str


class UserCreate(User):
    password: str  # 비밀번호는 평문으로 받음


class UserInKakao(User):
    thumbnail_image_url: HttpUrl
    profile_image_url: HttpUrl

    def dict(self, **kwargs):
        # HttpUrl을 문자열로 변환
        data = super().model_dump(**kwargs)
        data["thumbnail_image_url"] = str(data["thumbnail_image_url"])
        data["profile_image_url"] = str(data["profile_image_url"])
        return data
