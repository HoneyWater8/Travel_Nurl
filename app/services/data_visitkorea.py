from fastapi import HTTPException
from SPARQLWrapper import SPARQLWrapper, JSON

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
