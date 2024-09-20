from azure.cosmos import CosmosClient  # Azure Cosmos DB와 상호작용하기 위한 클라이언트
from azure.storage.blob import (
    BlobServiceClient,
    ContainerClient,
)  # Azure Blob Storage와 상호작용하기 위한 클라이언트
from dotenv import load_dotenv
from app.core.config import cosmos_settings

load_dotenv(dotenv_path="config.env")  # .env 파일의 환경 변수를 로드합니다.

# Cosmos DB 설정
cosmos_database_name = "ImageDatabase"  # 사용할 Cosmos DB 데이터베이스 이름
image_container_name = "ImageTable"  # 사용할 Cosmos DB 컨테이너 이름
embedding_container_name = "embedding-container-travelnuri"


## CLient를 가져오는 메소드
# Cosmos Client를 가져오는 메소드
def get_cosmos_client() -> CosmosClient:
    endpoint = cosmos_settings.COSMOS_END_POINT
    key = cosmos_settings.COSMOS_KEY

    if endpoint is None or key is None:
        raise ValueError(
            "COSMOS_END_POINT 또는 COSMOS_KEY 환경 변수가 설정되어야 합니다."
        )

    return CosmosClient(endpoint, key)


## Blob 클라이언트 서비스를 가져오는 메서드
def get_blob_service_client() -> BlobServiceClient:
    connection_string = cosmos_settings.COSMOS_BLOB_CONNECTION_KEY

    if connection_string is None:
        raise ValueError(
            "AZURE_STORAGE_CONNECTION_STRING 환경 변수가 설정되어야 합니다."
        )

    return BlobServiceClient.from_connection_string(connection_string)


## 컨테이너를 가져오는 메서드
def get_blob_container_client() -> ContainerClient:
    blob_service_client = get_blob_service_client()
    return blob_service_client.get_container_client(image_container_name)


## 컨테이너를 가져오는 메서드
def get_blob_container_client2() -> ContainerClient:
    blob_service_client = get_blob_service_client()
    return blob_service_client.get_container_client(embedding_container_name)
