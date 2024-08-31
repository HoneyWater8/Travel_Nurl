from fastapi import APIRouter, HTTPException
from app.services.data_visitkorea import execute_sparql_query

router = APIRouter()

SPARQL_ENDPOINT = "http://data.visitkorea.or.kr/sparql"

PREFIX = """    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX dc: <http://purl.org/dc/elements/1.1/>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX vi: <http://www.saltlux.com/transformer/views#>
    PREFIX kto: <http://data.visitkorea.or.kr/ontology/>
    PREFIX ktop: <http://data.visitkorea.or.kr/property/>
    PREFIX ids: <http://data.visitkorea.or.kr/resource/>
    PREFIX wgs: <http://www.w3.org/2003/01/geo/wgs84_pos#>
    PREFIX f: <http://www.saltlux.com/geo/functions#>
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    PREFIX geo: <http://www.saltlux.com/geo/property#>
"""


@router.get("/api/get_detail_place")
async def get_detail_place(place_name: str):
    query = f"""
{PREFIX}

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
        data = await execute_sparql_query(SPARQL_ENDPOINT, query)
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
