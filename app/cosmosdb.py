from azure.cosmos import CosmosClient  # Azure Cosmos DB와 상호작용하기 위한 클라이언트
from azure.storage.blob import (
    BlobServiceClient,
)  # Azure Blob Storage와 상호작용하기 위한 클라이언트
from app.core.config import settings  # settings 모듈에서 SERVICE_KEY 가져오기

# Cosmos DB 설정
cosmos_endpoint = (
    "https://suheonchoi1.documents.azure.com:443/"  # Cosmos DB 엔드포인트 URL
)
cosmos_key = settings.COSMOS_KEY  # Cosmos DB 액세스 키
cosmos_database_name = "ImageDatabase"  # 사용할 Cosmos DB 데이터베이스 이름
image_container_name = "ImageTable"  # 사용할 Cosmos DB 컨테이너 이름

# Blob Storage 설정
connection_string = "DefaultEndpointsProtocol=https;AccountName=suheonchoi1;AccountKey=uZ10rRIn+q3cbHd04iimIZY38pcda1ePeyyDbe1YEG9WkCQsu+6WXj2EsOw3mwMzWP4MVfRwkejj+AStg0UJYg==;EndpointSuffix=core.windows.net"  # Azure Blob Storage 연결 문자열
blob_service_client = BlobServiceClient.from_connection_string(
    connection_string
)  # Blob 서비스 클라이언트 생성
blob_container_client = blob_service_client.get_container_client(
    "image-container"
)  # Blob 컨테이너 클라이언트 생성
