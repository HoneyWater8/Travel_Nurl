from fastapi import APIRouter, HTTPException
from app.services.data_visitkorea import execute_sparql_query

router = APIRouter(prefix="/api", tags=["Tourapi"])


@router.get("/get_detail_place")
async def get_detail_place(place_name: str):
    """
    # Tourapi 데이터 베이스로부터 지역 정보를 가져오는 api
    - place_name: 찾으려고 하는 장소의 이름.
    """

    query = f"""

SELECT ?name ?address ?petsAvailable ?tel ?creditCard ?parking ?lat ?long (GROUP_CONCAT(?depiction; separator=", ") AS ?depictions)
WHERE {{
    ?resource a kto:Place ;
               foaf:name ?name ;
               ktop:address ?address ;
               rdfs:label "{place_name}"@ko .

    OPTIONAL {{ ?resource ktop:petsAvailable ?petsAvailable }}
    OPTIONAL {{ ?resource ktop:tel ?tel }}
    OPTIONAL {{ ?resource ktop:creditCard ?creditCard }}
    OPTIONAL {{ ?resource ktop:parking ?parking }}
    OPTIONAL {{ ?resource wgs:lat ?lat }}
    OPTIONAL {{ ?resource wgs:long ?long }}
    OPTIONAL {{ ?resource foaf:depiction ?depiction }}
}}
GROUP BY ?name ?address ?petsAvailable ?tel ?creditCard ?parking ?lat ?long
"""
    try:
        data = await execute_sparql_query(query)
        # 결과 파싱 및 JSON 형태로 변환
        parsed_data = []

        for result in data["results"]["bindings"]:
            entry = {
                "name": result.get("name", {}).get("value", "정보 없음"),
                "address": result.get("address", {}).get("value", "정보 없음"),
                "pets_available": result.get("petsAvailable", {}).get(
                    "value", "정보 없음"
                ),  # 애견 동반 가능 여부
                "telephone": result.get("tel", {}).get("value", "정보 없음"),
                "credit_card": result.get("creditCard", {}).get("value", "정보 없음"),
                "parking": result.get("parking", {}).get("value", "정보 없음"),
                "x": result.get("lat", {}).get("value", "정보 없음"),
                "y": result.get("long", {}).get("value", "정보 없음"),
                "image_url": (
                    result.get("depictions", {}).get("value", "").split(", ")
                    if result.get("depictions")
                    else []
                ),
            }
            parsed_data.append(entry)
        return parsed_data
    except HTTPException as e:
        raise e  # HTTPException을 그대로 전달
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
