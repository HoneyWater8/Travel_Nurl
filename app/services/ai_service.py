""" import numpy as np
import pandas as pd
import torch
import cv2
from retinaface import RetinaFace
from PIL import Image
import torchvision.models as models
import torchvision.transforms as transforms
from konlpy.tag import Okt
from sklearn.metrics.pairwise import cosine_similarity
from pathlib import Path
from app.cosmosdb import (
    get_cosmos_client,
    get_blob_container_client,
    get_blob_container_client2,
    cosmos_database_name,
    image_container_name,
)
import io
import aiohttp


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

        self.all_image_embeddings = None
        self.embeddings_df = None
        self.keywords_df = None

        self.okt = Okt()

    async def _load_embedding(self):
        try:
            async with aiohttp.ClientSession() as session:
                blob_client = self.blob_container_client2.get_blob_client(
                    "Embeddings.npy"
                )
                blob_data = blob_client.download_blob().readall()
                return np.load(io.BytesIO(blob_data))
        except Exception as e:
            print(f"Error loading embeddings: {e}")
            return None

    async def _load_embedding_csv(self):
        try:
            async with aiohttp.ClientSession() as session:
                blob_client = self.blob_container_client2.get_blob_client(
                    "Embeddings.csv"
                )
                blob_data = blob_client.download_blob().readall()
                return pd.read_csv(io.BytesIO(blob_data))
        except Exception as e:
            print(f"Error loading embeddings CSV: {e}")
            return None

    async def _load_place(self):
        try:
            async with aiohttp.ClientSession() as session:
                blob_client = self.blob_container_client2.get_blob_client("1_13023.csv")
                blob_data = blob_client.download_blob().readall()
                return pd.read_csv(io.BytesIO(blob_data))
        except Exception as e:
            print(f"Error loading place data: {e}")
            return None

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
        return set(word for word in nouns_and_adjectives if word not in stopwords)

    async def retrieve_image_names_from_cosmos(self, image_ids):
        image_names = {}
        for image_id in image_ids:
            query = f"SELECT * FROM c WHERE c.ImageID = {image_id}"
            items = list(
                self.image_container.query_items(
                    query, enable_cross_partition_query=True
                )
            )
            if items:
                image_names[image_id] = items[0]["ImageName"]
            else:
                print(f"No image name found for ImageID {image_id}")

        return image_names

    def blur_faces(self, image):
        img_array = np.array(image)
        faces = RetinaFace.detect_faces(img_array)

        if isinstance(faces, dict):
            for face in faces.values():
                facial_area = face["facial_area"]
                x1, y1, x2, y2 = facial_area

                mask = np.zeros_like(img_array, dtype=np.uint8)
                mask = cv2.ellipse(
                    mask,
                    ((x1 + x2) // 2, (y1 + y2) // 2),
                    ((x2 - x1) // 2, (y2 - y1) // 2),
                    0,
                    0,
                    360,
                    (255, 255, 255),
                    -1,
                )

                blurred_face = cv2.GaussianBlur(img_array[y1:y2, x1:x2], (99, 99), 30)

                img_array = cv2.bitwise_and(img_array, 255 - mask)
                mask_face = cv2.bitwise_and(blurred_face, mask[y1:y2, x1:x2])
                img_array[y1:y2, x1:x2] += mask_face

        return Image.fromarray(img_array)

    async def find_similar_image(
        self,
        user_image_path: str = "",
        user_text: str = "",
        region_ids: str = "",
        category_ids: str = "",
        top_N: int = 5,
    ):
        try:
            self.all_image_embeddings = await self._load_embedding()
            self.embeddings_df = await self._load_embedding_csv()
            self.keywords_df = await self._load_place()
        except Exception as e:
            print(f"Error loading data: {e}")
            return None

        if self.embeddings_df is None:
            print("Embeddings DataFrame is None.")
            return None

        if self.all_image_embeddings is None:
            print("All image embeddings are None.")
            return None

        if self.keywords_df is None:
            print("Keywords DataFrame is None.")
            return None

        user_image_features = await self.get_image_features(user_image_path)
        if user_image_features is None:
            return

        image_id_to_index = {
            image_id: idx for idx, image_id in enumerate(self.embeddings_df["ImageID"])
        }

        relevant_embeddings_df = self.embeddings_df
        if region_ids:
            region_ids_set = set(map(int, region_ids.split(",")))
            relevant_embeddings_df = relevant_embeddings_df[
                relevant_embeddings_df["RegionID"].isin(region_ids_set)
            ]

        if category_ids:
            category_ids_set = set(map(int, category_ids.split(",")))
            relevant_embeddings_df = relevant_embeddings_df[
                relevant_embeddings_df["CategoryID"].isin(category_ids_set)
            ]

        filtered_image_ids = relevant_embeddings_df["PlaceID"].tolist()
        filtered_keywords_df = self.keywords_df[
            self.keywords_df["PlaceID"].isin(filtered_image_ids)
        ]

        if user_text:
            user_keyword = self.extract_nouns_and_adjectives(user_text)
            filtered_keywords_df = filtered_keywords_df[
                filtered_keywords_df["개요"]
                .fillna("")
                .apply(lambda x: any(noun in x for noun in user_keyword))
                | filtered_keywords_df["명칭"]
                .fillna("")
                .apply(lambda x: any(noun in x for noun in user_keyword))
            ]

            if filtered_keywords_df.empty:
                print("No relevant keywords found.")
                return None

            relevant_place_ids = filtered_keywords_df["PlaceID"].unique()
            relevant_embeddings_df = self.embeddings_df[
                self.embeddings_df["PlaceID"].isin(relevant_place_ids)
            ]

            if relevant_embeddings_df.empty:
                print("No relevant embeddings found after keyword filtering.")
                return None

        relevant_image_ids = relevant_embeddings_df["ImageID"].tolist()
        relevant_indices = [
            image_id_to_index[image_id]
            for image_id in relevant_image_ids
            if image_id in image_id_to_index
        ]
        relevant_embeddings = self.all_image_embeddings[relevant_indices]

        similarity_scores = cosine_similarity(relevant_embeddings, user_image_features)

        top_N_indices = np.argsort(similarity_scores.flatten())[-top_N:]
        top_image_ids = [
            relevant_embeddings_df.iloc[idx]["ImageID"] for idx in top_N_indices
        ]

        # Cosmos DB에서 ImageName을 조회
        return await self.retrieve_image_names_from_cosmos(top_image_ids)
 """
