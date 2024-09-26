from typing import Optional
from fastapi import HTTPException
from SPARQLWrapper import SPARQLWrapper, JSON
from app.schemas.place import PlaceInfo, ImageBase, Place_detail

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


async def search_place(place_name: str, image_num: int = 5) -> Optional[Place_detail]:
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

        if not data["results"]["bindings"]:
            return None  # 결과가 없으면 None 반환

        result = data["results"]["bindings"][0]
        depictions = result.get("depictions", {}).get("value", "")
        images = [
            ImageBase(img_url=img_url.strip())
            for img_url in depictions.split(", ")
            if img_url
        ]

        return Place_detail(
            name=result.get("name", {}).get("value", place_name),
            address=result.get("address", {}).get("value", "정보 없음"),
            parking=result.get("parking", {}).get("value", "정보 없음"),
            petsAvailable=result.get("petsAvailable", {}).get("value", "정보 없음"),
            tel=result.get("tel", {}).get("value", "정보 없음"),
            x=result.get("lat", {}).get("value", 0.000),
            y=result.get("long", {}).get("value", 0.000),
            images=images,
        )
    except Exception as e:
        # 에러 로그 추가
        print(f"Error in search_place: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def search_places(num: int = 1):
    # SPARQL 쿼리 작성
    query = f"""
    SELECT ?resource ?name ?address ?description ?depiction
    WHERE {{
        ?resource a kto:Place ;
                rdfs:label ?name ;
                ktop:address ?address ;
                dc:description ?description ;
                foaf:depiction ?depiction .
        FILTER(
            (CONTAINS(lcase(?description), "관광") || 
            CONTAINS(lcase(?name), "관광")) &&
            (STRENDS(str(?depiction), ".jpg") || 
            STRENDS(str(?depiction), ".JPG") || 
            STRENDS(str(?depiction), ".png") || 
            STRENDS(str(?depiction), ".PNG") || 
            STRENDS(str(?depiction), ".gif") || 
            STRENDS(str(?depiction), ".GIF"))
        )
    }}
    ORDER BY RAND()
    LIMIT {num}
    """
    results = await execute_sparql_query(query)

    response: list[PlaceInfo] = []

    # 결과 파싱
    for result in results["results"]["bindings"]:
        resource = result.get("resource", {}).get("value", "None")
        name = result.get("name", {}).get("value", "None")
        address = result.get("address", {}).get("value", "None")
        description = result.get("description", {}).get("value", "None")
        depiction = result.get("depiction", {}).get("value", "None")
        # 이미지 객체 생성
        image = ImageBase(img_url=depiction)

        # PlaceInfo 객체 생성
        place = PlaceInfo(
            name=name,
            address=address,
            description=description,
            images=[image],  # 이미지 리스트에 추가
        )

        # 결과 리스트에 PlaceInfo 객체 추가
        response.append(place)
    return response


async def execute_sparql_query(query: str) -> dict:
    query = PREFIX + query
    sparql = SPARQLWrapper(SPARQL_ENDPOINT)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    try:
        response = sparql.query().convert()
        return response  # type: ignore
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
