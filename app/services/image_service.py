import numpy as np
from app.cosmosdb import retrieve_image_names_from_cosmos
from app.utils.helpers import get_image_features, display_images


def find_similar_image(user_image_path, user_text=None, top_N=5):
    user_image_features = get_image_features(user_image_path)
    if user_image_features is None:
        return {"error": "Failed to extract image features."}

    # 기존 로직을 여기에 포함
    # ...

    return {"similar_images": similar_images}
