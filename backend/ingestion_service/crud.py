import httpx
from ..app import schemas as main_app_schemas # Import schemas from the main app
from typing import Optional

MAIN_BACKEND_API_URL = "http://127.0.0.1:8000" # This should be configurable

async def create_article_in_main_backend(
    podcast_id: str,
    source_block_id: str,
    url: str,
    title: str,
    snippet: Optional[str] = None
):
    article_data = main_app_schemas.ArticleCreate(
        podcast_id=podcast_id,
        source_block_id=source_block_id,
        url=url,
        title=title,
        snippet=snippet
    ).model_dump_json() # Use model_dump_json for Pydantic v2

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{MAIN_BACKEND_API_URL}/articles/",
            headers={"Content-Type": "application/json"},
            content=article_data
        )
        response.raise_for_status() # Raise an exception for 4xx/5xx responses
        return response.json()
