from fastapi import APIRouter, HTTPException
from app.services.data_visitkorea import execute_sparql_query

router = APIRouter()

SPARQL_ENDPOINT = "http://data.visitkorea.or.kr/sparql"

@router.get("/api/get_detail_place")
async def search_place(place_name: str):
    query = f"""
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
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
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    PREFIX geo: <http://www.saltlux.com/geo/property#>
    PREFIX pf: <http://www.saltlux.com/DARQ/property#> 

    SELECT * 
        WHERE {{
        ?resource a kto:Place ;
            rdfs:label ?name . 
            FILTER (contains(?name, "{place_name.lower()}") ) 
        }} 
    LIMIT 10
    """
    try:
        results = await execute_sparql_query(SPARQL_ENDPOINT, query)
        return results
    except HTTPException as e:
        raise e  # HTTPException을 그대로 전달
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))