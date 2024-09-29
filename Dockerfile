# 베이스 이미지 설정
FROM python:3.11-slim

# Java JDK 설치
RUN apt-get update && apt-get install -y \
    default-jdk \
    && apt-get clean


# 작업 디렉토리 설정
WORKDIR /app

# 의존성 파일 복사
COPY requirements.txt .

# 의존성 설치
RUN pip install --no-cache-dir -r requirements.txt


# 프로젝트 파일 복사
COPY . .


# FastAPI 실행 (Gunicorn과 Uvicorn 사용)
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "app.main:app"]
