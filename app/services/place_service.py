import random
from azure.cosmos import CosmosClient
from app.cosmosdb import (
    get_cosmos_client,
    get_blob_container_client,
    cosmos_database_name,
    image_container_name,
)
from azure.cosmos import exceptions
from fastapi import HTTPException
from app.schemas.place import ImageInfo
from typing import List


class PlaceService:
    def __init__(self, cosmos_client: CosmosClient):
        self.cosmos_client = cosmos_client
        self.database = self.cosmos_client.get_database_client(cosmos_database_name)
        self.container = self.database.get_container_client(image_container_name)
        self.blob_container_client = get_blob_container_client()

    # 무작위 이미지 5개 가져오기
    async def get_random_images(self, num: int):
        try:
            query = f"SELECT VALUE COUNT(1) FROM c"
            result: int = list(
                self.container.query_items(query, enable_cross_partition_query=True)
            )[
                0
            ]  # type: ignore
        except exceptions.CosmosHttpResponseError as e:
            raise HTTPException(status_code=500, detail=f"Cosmos DB 오류: {e.message}")

        try:
            if result:
                selected_ids = random.sample(range(1, result + 1), min(num, result))

            # ID 목록을 사용하여 쿼리 생성
            id_list = ", ".join([f"'{id_}'" for id_ in selected_ids])  # type: ignore
            items_query = f"SELECT c.ImageName, c.PlaceName, c.ImageURL FROM c WHERE c.id IN ({id_list})"

            items = list(
                self.container.query_items(
                    items_query, enable_cross_partition_query=True
                )
            )

            if len(items) == 0:
                raise ValueError("사진이 없습니다.")
            if len(items) < num:
                raise ValueError(f"사진이 {num}개보다 적습니다.")

            # 이미지 정보를 담을 리스트
            places: List[ImageInfo] = []

            for item in items:
                image = ImageInfo(
                    img_name=item["ImageName"],
                    img_url=item["ImageURL"],
                    place_name=item["PlaceName"],
                )
                places.append(image)
            return places

        except exceptions.CosmosHttpResponseError as e:
            raise HTTPException(status_code=500, detail=f"Cosmos DB 오류: {e.message}")
        except ValueError as ve:
            print(ve)
            raise HTTPException(status_code=400, detail=str(ve))
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=str(e)
            )  # 일반 오류는 500으로 처리
