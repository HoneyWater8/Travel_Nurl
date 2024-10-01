from typing import Optional
import torch
from PIL import Image
import torchvision.models as models
import torchvision.transforms as transforms
from konlpy.tag import Okt
from pathlib import Path
from app.cosmosdb import (
    get_cosmos_client,
    get_blob_container_client,
    cosmos_database_name,
    image_container_name,
    blob_image_container_name,
)
from pinecone import Pinecone
from app.core.config import pinecone_settins
from app.schemas.place import Place_detail, blur_place
from app.services.data_visitkorea import search_place


class ImageAIService:
    def __init__(self):
        self.cosmos_client = get_cosmos_client()
        self.database = self.cosmos_client.get_database_client(cosmos_database_name)
        self.image_container = self.database.get_container_client(image_container_name)
        self.blob_image_container_client = get_blob_container_client(
            blob_image_container_name
        )
        self.resnet50_model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.preprocess = self._get_preprocess_transform()
        # Pinecone 초기화
        self.pc = Pinecone(api_key=pinecone_settins.key)
        self.pinecone_index = self.pc.Index(pinecone_settins.index_name)
        self.okt = Okt()

    async def _load_model(self):
        if self.resnet50_model is None:
            self.resnet50_model = models.resnet50(weights="DEFAULT").to(self.device)
            self.resnet50_model.eval()

    def _get_preprocess_transform(self):
        return transforms.Compose(
            [
                transforms.Resize(256),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
                ),
            ]
        )

    async def get_image_features(self, image_path):
        await self._load_model()
        try:
            image = Image.open(image_path).convert("RGB")
        except IOError as e:
            print(f"Error opening image: {e}")
            return None

        image_input = self.preprocess(image).unsqueeze(0).to(self.device)

        with torch.no_grad():
            if self.resnet50_model is not None:
                image_features = self.resnet50_model(image_input)
                return image_features.cpu().numpy()
            else:
                print("Model is not loaded.")
                return None

    def extract_nouns_and_adjectives(self, text):
        file_path = Path("app/AI/stopword_ko.txt")
        with open(file_path, encoding="utf-8") as f:
            stopwords = set(line.strip() for line in f)

        pos_tagged = self.okt.pos(text)
        nouns_and_adjectives = [
            word for word, pos in pos_tagged if pos in ["Noun", "Adjective"]
        ]
        return set(
            word for word in nouns_and_adjectives if word not in stopwords
        )  # 불용어 제외

    # Blob Storage에서 이미지를 다운로드하여 유사도 점수에 따라 정렬된 순서로 시각화하는 함수
    async def get_place_info(
        self,
        top_image_ids: list,
    ):
        places = []

        for i, image_id in enumerate(top_image_ids):
            image_id = int(image_id)
            query = (
                f"SELECT c.ImageName , c.PlaceName FROM c WHERE c.ImageID = {image_id}"
            )
            items = list(
                self.image_container.query_items(
                    query, enable_cross_partition_query=True
                )
            )

            if items:
                image_name = items[0]["ImageName"]
                place_name = items[0]["PlaceName"]
                print(f"Downloading and displaying image: {image_name}")
                # URL 인코딩
                blob_client = self.blob_image_container_client.get_blob_client(
                    image_name
                )
                try:
                    blob_client.get_blob_properties()  # Blob의 속성을 가져와서 존재 여부 확인
                    place: Optional[Place_detail] = await search_place(place_name)
                    if place:
                        place = blur_place(**place.model_dump())  # unpacking 사용
                        place.blur_image = blob_client.url
                    # 유사도 점수 및 추가 정보 표시
                    places.append(place)
                except Exception as e:
                    print(f"Blob not found or error occurred: {e}")
                    if place:
                        place = blur_place(**place.model_dump())  # unpacking 사용
                        place.blur_image = None  # Blob이 없으면 None 할당
                    places.append(place)
            else:
                print(f"No image found for ImageID: {image_id}")
                return
        return places

    async def find_similar_image(
        self,
        user_image_path: str = "",
        user_text: str = "",
        region_id: str = "",
        category_id: str = "",
        top_N: int = 5,
    ):

        # 이미지 특성 추출
        user_image_features = await self.get_image_features(user_image_path)
        if user_image_features is None:
            print("Failed to extract image features. Exiting.")
            return

        # Pinecone에서 필터 조건에 맞는 전체 결과 검색
        query_results = self.pinecone_index.query(
            vector=user_image_features.flatten().tolist(),
            top_k=10000,  # 최대 10,000개의 결과를 가져옴
            include_metadata=True,
        )

        filtered_count = len(query_results["matches"])
        print(f"Initial results count: {filtered_count}")

        if filtered_count == 0:
            print("No relevant images found based on the provided filters.")
            return

        # RegionID 필터링
        if region_id:
            region_ids_set = set(map(str, region_id.split(",")))
            query_results["matches"] = [
                match
                for match in query_results["matches"]
                if match["metadata"].get("RegionID") in region_ids_set
            ]
            print(
                f"Filtered results count after RegionID filter: {len(query_results['matches'])}"
            )

        # CategoryID 필터링
        if category_id:
            category_ids_set = set(map(str, category_id.split(",")))
            query_results["matches"] = [
                match
                for match in query_results["matches"]
                if match["metadata"].get("CategoryID") in category_ids_set
            ]
            print(
                f"Filtered results count after CategoryID filter: {len(query_results['matches'])}"
            )

        # 텍스트 필터링을 위해 overview를 가져옴
        filtered_matches = query_results["matches"]  # 기본적으로 필터링된 이미지 목록

        user_keywords = self.extract_nouns_and_adjectives(user_text)
        if len(user_keywords) == 0:
            print("No nouns or adjectives recognized.")
            print("Ignoring user_text.")

        if user_text and user_keywords:  # user_text가 있을 때만 필터링 수행
            # overview 기반 필터링
            filtered_matches = [
                match
                for match in filtered_matches
                if any(
                    keyword in match["metadata"].get("overview", "")
                    for keyword in user_keywords
                )
            ]

        final_filtered_count = len(filtered_matches)
        print(
            f"Filtered results count after applying text filter: {final_filtered_count}"
        )

        if final_filtered_count == 0:
            print("No relevant images found after text-based filtering.")
            return

        # 최종 상위 N개의 결과로 제한
        top_image_ids = []
        top_N_scores = []
        place_ids = []
        region_ids = []
        category_ids = []

        for match in filtered_matches[:top_N]:
            top_image_ids.append(match["id"])
            top_N_scores.append(match["score"])
            place_ids.append(match["metadata"].get("PlaceID"))
            region_ids.append(match["metadata"].get("RegionID"))
            category_ids.append(match["metadata"].get("CategoryID"))

        print(f"Top {top_N} most similar images found after all filters:")
        for image_id, score in zip(top_image_ids, top_N_scores):
            print(f"ImageID: {image_id}, Similarity Score: {score}")

        return await self.get_place_info(top_image_ids)
