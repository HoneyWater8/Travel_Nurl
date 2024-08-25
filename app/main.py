from fastapi import FastAPI, HTTPException
from app.routers import place, user, external, visitkorea
from app.database import ping_mongodb
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS 설정
origins = [
    "http://127.0.0.1:8000",
    "http://localhost:8000",  # FastAPI 서버 주소
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 포함
app.include_router(place.router)
app.include_router(external.router)  # 외부 API 라우터 포함
app.include_router(visitkorea.router)
app.include_router(user.router)


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
