import numpy as np
import torch
import cv2
from retinaface import RetinaFace
from PIL import Image
import torchvision.models as models
import torchvision.transforms as transforms
from konlpy.tag import Okt
from pathlib import Path
from app.cosmosdb import (
    get_cosmos_client,
    get_blob_container_client,
    get_blob_container_client2,
    cosmos_database_name,
    image_container_name,
)
from pinecone import Pinecone
from app.core.config import pinecone_settins


class ImageAIService:
    def __init__(self):
        self.cosmos_client = get_cosmos_client()
        self.database = self.cosmos_client.get_database_client(cosmos_database_name)
        self.image_container = self.database.get_container_client(image_container_name)
        self.blob_container_client = get_blob_container_client()
        self.blob_container_client2 = get_blob_container_client2()
        self.resnet50_model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.preprocess = self._get_preprocess_transform()
        # Pinecone 초기화
        self.pc = Pinecone(api_key=pinecone_settins.key)
        self.pinecone_index = self.pc.Index(pinecone_settins.index_name)
        self.okt = Okt()

    def _load_model(self):
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
        self._load_model()
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

    def blur_faces(self, image):
        img_array = np.array(image)

        # RetinaFace를 사용하여 얼굴 감지
        faces = RetinaFace.detect_faces(img_array)

        if isinstance(faces, dict):  # 감지된 얼굴이 있을 경우
            for face_key in faces.keys():
                face = faces[face_key]
                facial_area = face["facial_area"]
                x1, y1, x2, y2 = facial_area

                # 얼굴 중심점과 크기 계산
                center_x, center_y = (x1 + x2) // 2, (y1 + y2) // 2
                width, height = x2 - x1, y2 - y1

                # 원형 또는 타원형 마스크 생성 (이 예제에서는 타원형)
                mask = np.zeros_like(img_array, dtype=np.uint8)
                mask = cv2.ellipse(
                    mask,
                    (center_x, center_y),
                    (width // 2, height // 2),
                    0,
                    0,
                    360,
                    (255, 255, 255),
                    -1,
                )

                # 블러 처리된 얼굴 영역
                blurred_face = cv2.GaussianBlur(img_array[y1:y2, x1:x2], (99, 99), 30)

                # 원형 또는 타원형 마스크를 적용하여 블러 처리된 얼굴과 원본 이미지 합성
                img_array = cv2.bitwise_and(img_array, 255 - mask)
                mask_face = cv2.bitwise_and(blurred_face, mask[y1:y2, x1:x2])
                img_array[y1:y2, x1:x2] += mask_face

        return Image.fromarray(img_array)

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

        return {
            "top_image_ids": top_image_ids,
            "top_N_scores": top_N_scores,
            "place_ids": place_ids,
            "region_ids": region_ids,
            "category_ids": category_ids,
        }
