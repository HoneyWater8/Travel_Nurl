from azure.cosmos import CosmosClient  # Azure Cosmos DB와 상호작용하기 위한 클라이언트
from azure.storage.blob import (
    BlobServiceClient,
)  # Azure Blob Storage와 상호작용하기 위한 클라이언트
from app.core.config import settings  # settings 모듈에서 SERVICE_KEY 가져오기

# Cosmos DB 설정
cosmos_database_name = "ImageDatabase"  # 사용할 Cosmos DB 데이터베이스 이름
image_container_name = "ImageTable"  # 사용할 Cosmos DB 컨테이너 이름


## CLient를 가져오는 메소드
def get_cosmos_client():
    return CosmosClient(settings.COSMOS_END_POINT, settings.COSMOS_KEY)


## Blob 클라이언트 서비스를 가져오는 메서드
def get_blob_service_client():
    return BlobServiceClient.from_connection_string(settings.COSMOS_BLOB_CONNECTION_KEY)


## 컨테이너를 가져오는 메서드
def get_blob_container_client():
    blob_service_client = get_blob_service_client()
    return blob_service_client.get_container_client(image_container_name)
