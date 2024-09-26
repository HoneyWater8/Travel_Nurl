# from pymongo import MongoClient
# from azure.cosmos import CosmosClient
# from azure.storage.blob import BlobServiceClient
# from models.photo import PhotoMetadata
# from datetime import datetime
# from fastapi import UploadFile
# import os
# import shutil
# from app.database import search_history_collection, favorite_collection
# from app.cosmosdb import get_blob_container_client, blob_record_container_name


# class RecordService:
#     def __init__(self):
#         os.makedirs("uploads", exist_ok=True)
#         self.record_blob_client = get_blob_container_client(blob_record_container_name)

#     async def upload_photo(self, user_id: str, file: UploadFile):
#         user_folder = f"uploads/{user_id}"
#         os.makedirs(user_folder, exist_ok=True)

#         temp_file_path = os.path.join(user_folder, f"temp_{file.filename}")

#         with open(temp_file_path, "wb") as buffer:
#             shutil.copyfileobj(file.file, buffer)

#         # Azure Blob Storage에 파일 업로드
#         with open(temp_file_path, "rb") as data:
#             blob_client.upload_blob(f"{user_id}/{file.filename}", data)

#         timestamp = datetime.utcnow()
#         metadata = PhotoMetadata(filename=file.filename, timestamp=timestamp)

#         # MongoDB에 메타데이터 저장
#         mongo_record = {
#             "user_id": user_id,
#             "filename": file.filename,
#             "timestamp": timestamp,
#         }
#         mongo_collection.insert_one(mongo_record)

#         # Azure Cosmos DB에 메타데이터 저장
#         cosmos_record = {
#             "id": str(mongo_record["_id"]),
#             "user_id": user_id,
#             "filename": file.filename,
#             "timestamp": timestamp.isoformat(),
#         }
#         cosmos_container.upsert_item(cosmos_record)

#         os.remove(temp_file_path)

#         return {"filename": file.filename, "timestamp": timestamp}

#     async def get_upload_history(self, user_id: str):
#         mongo_history = list(mongo_collection.find({"user_id": user_id}))
#         cosmos_history = list(
#             cosmos_container.query_items(
#                 query=f"SELECT * FROM c WHERE c.user_id = '{user_id}'",
#                 enable_cross_partition_query=True,
#             )
#         )

#         return {"mongo_history": mongo_history, "cosmos_history": cosmos_history}

#     async def save_search_history(self, user_id: str, query: str):
#         timestamp = datetime.utcnow()
#         search_record = {"user_id": user_id, "query": query, "timestamp": timestamp}
#         mongo_collection.insert_one(search_record)

#     async def get_search_history(self, user_id: str):
#         search_history = list(mongo_collection.find({"user_id": user_id}))
#         return search_history

#     async def add_favorite(self, user_id: str, filename: str):
#         timestamp = datetime.utcnow()
#         favorite_record = {
#             "user_id": user_id,
#             "filename": filename,
#             "timestamp": timestamp,
#         }
#         mongo_collection.insert_one(favorite_record)

#     async def get_favorites(self, user_id: str):
#         favorites = list(mongo_collection.find({"user_id": user_id}))
#         return favorites
