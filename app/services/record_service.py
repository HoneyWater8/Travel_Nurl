from app.models.record import SearchHistory
from app.schemas.place import blur_place
from datetime import datetime
from fastapi import UploadFile
import os
import uuid
import shutil
from app.database import search_history_collection, favorite_collection
from app.cosmosdb import (
    storage_account,
    blob_record_container_name,
    get_blob_container_client,
)
import mimetypes
from azure.storage.blob import ContentSettings


class RecordService:
    def __init__(self):
        os.makedirs("uploads", exist_ok=True)
        self.record_blob_client = get_blob_container_client(blob_record_container_name)
        self.storage_account = storage_account
        self.record_container_name = blob_record_container_name

    async def save_search_history(self, user_id: str, file: UploadFile):
        # 사용자 문서가 없으면 생성
        await favorite_collection.update_one(
            {"user_id": user_id},  # 사용자 문서를 찾는 조건
            {"$setOnInsert": {"history": []}},  # 문서가 없으면 favorites 배열을 초기화
            upsert=True,  # 문서가 없으면 새로 생성
        )

        # 파일 확인
        if file is None or file.filename is None:
            print("No file uploaded or file has no name.")
            return

        user_folder = f"uploads/{user_id}"
        os.makedirs(user_folder, exist_ok=True)

        # 임시 파일 경로 설정
        temp_file_path = os.path.join(user_folder, f"temp_{file.filename}")

        # 파일 저장
        try:
            with open(temp_file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            timestamp = datetime.utcnow()

            # 새로운 파일 이름 생성 (UUID 사용)
            new_file_name = f"{user_id}/{uuid.uuid4()}.{file.filename.split('.')[-1]}"
            # MIME 타입 자동 설정
            mime_type, _ = mimetypes.guess_type(file.filename)
            if mime_type is None:
                mime_type = "application/octet-stream"  # 기본 MIME 타입 설정

            # Azure Blob Storage에 파일 업로드
            with open(temp_file_path, "rb") as data:
                self.record_blob_client.upload_blob(
                    new_file_name,
                    data,
                    content_settings=ContentSettings(content_type=mime_type),
                )

            # 업로드된 파일의 URL 생성
            img_url = f"https://{self.storage_account}.blob.core.windows.net/{self.record_container_name}/{new_file_name}"

            # 검색 기록 메타데이터 생성
            search_history = SearchHistory(
                img_name=new_file_name,
                img_url=img_url,
                user_id=user_id,
                timestamp=timestamp,
            )

            # MongoDB에 메타데이터 저장
            # 즐겨찾기 추가
            await favorite_collection.update_one(
                {"user_id": user_id},  # 사용자 문서 찾기
                {
                    "$addToSet": {"history": search_history.model_dump()}
                },  # 중복 추가 방지
            )
            return temp_file_path

        except Exception as e:
            print(f"Error uploading file: {e}")


    async def get_search_history(self, user_id: str):
        mongo_history = await favorite_collection.find_one(
            {"user_id": user_id}, {"_id": 0, "history": 1}
        )
        return {f"{user_id}'s search_history": mongo_history}

    async def add_favorite(self, user_id: str, place: dict):
        # 이미 추가된 blur_image 확인
        existing_favorite = await favorite_collection.find_one(
            {"user_id": user_id, "favorites.blur_image": place["blur_image"]}
        )

        if existing_favorite:
            return False  # 이미 추가된 경우

        timestamp = datetime.utcnow()

        # 즐겨찾기 기록 객체
        place["timestamp"] = timestamp  # 타임스탬프 추가

        # 사용자 문서가 없으면 생성
        await favorite_collection.update_one(
            {"user_id": user_id},  # 사용자 문서를 찾는 조건
            {
                "$setOnInsert": {"favorites": []}
            },  # 문서가 없으면 favorites 배열을 초기화
            upsert=True,  # 문서가 없으면 새로 생성
        )

        # 즐겨찾기 추가
        await favorite_collection.update_one(
            {"user_id": user_id},  # 사용자 문서 찾기
            {"$addToSet": {"favorites": place}},  # 중복 추가 방지
        )
        return True  # 추가 성공

    async def remove_favorite(self, user_id: str, blur_image: str):
        # MongoDB에서 사용자의 즐겨찾기 목록에서 place_name을 삭제하는 로직
        result = await favorite_collection.update_one(
            {"user_id": user_id},
            {"$pull": {"favorites": {"blur_image": blur_image}}},  # blur_image로 삭제
        )
        return result.modified_count > 0  # 삭제 성공 여부 반환

    async def get_favorites(self, user_id: str):
        # 사용자의 즐겨찾기 목록을 가져오는 로직
        user_favorites = await favorite_collection.find_one(
            {"user_id": user_id}, {"_id": 0, "favorites": 1}
        )
        return (
            user_favorites.get("favorites", []) if user_favorites else []
        )  # 즐겨찾기가 없으면 빈 리스트 반환
