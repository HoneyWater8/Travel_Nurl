import httpx
from fastapi import HTTPException

async def execute_sparql_query(endpoint: str, query: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            endpoint,
            data={'query': query},
            headers={'Accept': 'application/sparql-results+json'}
        )
        
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)