from fastapi import HTTPException
from SPARQLWrapper import SPARQLWrapper, JSON


async def execute_sparql_query(end_point: str, query: str) -> dict:
    sparql = SPARQLWrapper(end_point)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    try:
        response = sparql.query().convert()
        return response  # type: ignore
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
