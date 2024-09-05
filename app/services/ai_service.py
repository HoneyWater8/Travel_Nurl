""" import numpy as np
import pandas as pd
import torch
from PIL import Image
from torchvision import models, transforms
from konlpy.tag import Okt
from sklearn.metrics.pairwise import cosine_similarity
import ast
from azure.cosmos import CosmosClient
from app.core.config import settings
from pathlib import Path
from app.cosmosdb import cosmos_database_name, cosmos_endpoint, image_container_name

# ResNet50 모델과 디바이스 설정
device = "cuda" if torch.cuda.is_available() else "cpu"
resnet50_model = models.resnet50(weights="DEFAULT").to(device)
resnet50_model.eval()


# 이미지 전처리 설정
preprocess = transforms.Compose(
    [
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ]
)

# 파일 경로 설정
embeddings_csv_path = Path("app/AI/Embeddings.csv")
keywords_csv_path = Path("app/AI/1_810.csv")

# 임베딩 및 키워드 데이터 로드
embeddings_df = pd.read_csv(embeddings_csv_path)
keywords_df = pd.read_csv(keywords_csv_path)
okt = Okt()


def parse_embeddings(embedding_str):
    try:
        return np.array(ast.literal_eval(embedding_str))
    except (ValueError, SyntaxError):
        return np.array([])


embeddings_df["ImageEmbeddings"] = embeddings_df["ImageEmbeddings"].apply(parse_embeddings)  # type: ignore 해당 부분 주의하기
all_image_embeddings = np.vstack(embeddings_df["ImageEmbeddings"].values)  # type: ignore


class AiService:
    @staticmethod
    def get_image_features(image_path):
        image = Image.open(image_path).convert("RGB")
        image_input = preprocess(image).unsqueeze(0).to(device)
        with torch.no_grad():
            image_features = resnet50_model(image_input)
        return image_features.cpu().numpy()

    @staticmethod
    def extract_nouns(text):
        return set(okt.nouns(text))

    @staticmethod
    def retrieve_image_info_from_cosmos(image_ids):
        cosmos_client = CosmosClient(cosmos_endpoint, settings.COSMOS_KEY)
        database = cosmos_client.get_database_client(cosmos_database_name)
        image_container = database.get_container_client(image_container_name)
        image_names = {}
        for image_id in image_ids:
            query = f"SELECT * FROM c WHERE c.ImageID = {image_id}"
            items = list(
                image_container.query_items(query, enable_cross_partition_query=True)
            )
            if items:
                image_names[image_id] = {
                    "ImageName": items[0]["ImageName"],
                    "PlaceName": items[0][
                        "PlaceName"
                    ],  # items[0]에서 PlaceName을 가져옴
                    "ImageUrl": items[0]["ImageURL"],
                }
        return image_names

    @staticmethod
    def find_similar_image(user_image_path, user_text=None, top_N=5):
        # 이미지 특징 추출
        user_image_features = PlaceService.get_image_features(user_image_path)

        # 기본적으로 모든 임베딩을 포함
        relevant_embeddings_df = embeddings_df

        if user_text:
            # 사용자 텍스트에서 명사 추출
            user_nouns = PlaceService.extract_nouns(user_text)

            # 개요 열을 필터링하여 명사 포함 여부 확인
            keywords_df["개요"] = keywords_df["개요"].fillna(
                ""
            )  # 개요 열의 결측값을 빈 문자열로 채움
            filtered_keywords_df = keywords_df[
                keywords_df["개요"].apply(
                    lambda x: any(noun in x for noun in user_nouns)
                )
            ]  # 사용자가 입력한 명사와 일치하는 개요 필터링

            if not filtered_keywords_df.empty:
                # 필터링된 키워드에 해당하는 PlaceID 추출
                relevant_place_ids = filtered_keywords_df["PlaceID"].unique()

                # 해당 PlaceID를 가진 임베딩만 필터링
                relevant_embeddings_df = embeddings_df[
                    embeddings_df["PlaceID"].isin(relevant_place_ids)
                ].reset_index(drop=True)

            # 관련 이미지 임베딩을 수직으로 쌓아 numpy 배열로 변환
        relevant_embeddings = np.vstack(relevant_embeddings_df["ImageEmbeddings"].values)  # type: ignore

        # 사용자 이미지와 관련 이미지 간의 코사인 유사도 계산
        similarity_scores = cosine_similarity(relevant_embeddings, user_image_features)

        # 유사도 점수를 기준으로 인덱스를 정렬하고 상위 N개의 인덱스 선택
        top_N_indices = np.argsort(similarity_scores.flatten())[-top_N:]

        # 상위 N개의 유사도 점수 추출
        top_N_scores = similarity_scores.flatten()[top_N_indices]

        # 상위 N개의 인덱스를 사용하여 해당 이미지 ID 추출
        top_image_ids = relevant_embeddings_df.iloc[top_N_indices]["ImageID"].tolist()

        # 추출한 이미지 ID를 사용하여 이미지 이름과 장소 이름을 가져옴
        image_names = PlaceService.retrieve_image_info_from_cosmos(top_image_ids)

        # 이미지 이름과 상위 N개의 유사도 점수를 반환
        return image_names, top_N_scores
 """
