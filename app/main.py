from fastapi import FastAPI, HTTPException
from app.routers import (
    user_router,
    external_router,
    place_router,
    visitkorea_router,
    ai_router,
    history_router,
)
from app.database import ping_mongodb
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from app.core.config import base_settings

app = FastAPI()

session_key = base_settings.SERVICE_KEY
if session_key is None:
    raise ValueError("SESSION_KEY 환경 변수가 설정되어야 합니다.")


## session 관리를 위한 추가.
app.add_middleware(SessionMiddleware, secret_key=session_key)

## 다른 도메인에서 호스팅되는 리소스에 접근할 수 있도록 하기 위함.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://www.travelnuri.site",
        "http://www.travelnuri.site"
    ],  # 허용할 출처
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 포함
app.include_router(history_router)
app.include_router(ai_router)
app.include_router(external_router)  # 외부 API 라우터 포함
app.include_router(place_router)
app.include_router(user_router)
app.include_router(visitkorea_router)


@app.get("/ping")
def ping_mongodb_endpoint():
    if ping_mongodb():
        return {
            "message": "Pinged your deployment. You successfully connected to MongoDB!"
        }
    else:
        return HTTPException(
            status_code=500, detail={"error": "Failed to connect to MongoDB"}
        )


@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI application!"}


@app.get("/health")
async def health_check():
    # MongoDB 상태 검사
    try:
        await ping_mongodb()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MongoDB Unhealthy: {str(e)}")

    return {"status": "healthy"}
