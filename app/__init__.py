""" # app/__init__.py

from .database import engine, SessionLocal
from .models import Base

# 데이터베이스 테이블 생성
def init_db():
    Base.metadata.create_all(bind=engine)

init_db()  # 애플리케이션 시작 시 데이터베이스 초기화 """