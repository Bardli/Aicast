from fastapi import FastAPI, HTTPException
import logging
from logging.handlers import RotatingFileHandler
from typing import List, Optional, Dict, Any
import aiohttp
from bs4 import BeautifulSoup
import feedparser

from . import schemas, crud

# --- Logging Configuration ---
log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log_file = "ingestion_service.log"

# Use RotatingFileHandler for log rotation
file_handler = RotatingFileHandler(log_file, maxBytes=1024 * 1024 * 5, backupCount=2) # 5MB per file
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.INFO)

# Get root logger and add handler
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)

app = FastAPI(
    title="Content Ingestion Service",
    description="Service for fetching and normalizing news content.",
    version="0.1.0",
)

@app.on_event("startup")
async def startup_event():
    logger.info("--- Content Ingestion Service startup ---")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("--- Content Ingestion Service shutdown ---")

@app.get("/")
def read_root():
    return {"message": "Content Ingestion Service is running"}


# --- Ingestion Logic ---

async def ingest_rss(rule: schemas.IngestionRule, podcast_id: str, source_block_id: str):
    logger.info(f"Ingesting RSS from: {rule.url}")
    articles = []
    try:
        feed = feedparser.parse(rule.url)
        for entry in feed.entries:
            title = entry.title
            link = entry.link
            summary = getattr(entry, 'summary', getattr(entry, 'description', None))
            
            # Create article in main backend
            await crud.create_article_in_main_backend(
                podcast_id=podcast_id,
                source_block_id=source_block_id,
                url=link,
                title=title,
                snippet=summary
            )
            logger.info(f"Ingested RSS article: {title}")
    except Exception as e:
        logger.error(f"Error ingesting RSS from {rule.url}: {e}", exc_info=True)
    return articles

async def ingest_api(rule: schemas.IngestionRule, podcast_id: str, source_block_id: str):
    logger.info(f"Ingesting API from: {rule.url}")
    articles = []
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(rule.url) as response:
                response.raise_for_status()
                data = await response.json()
                # This is a generic API ingestion. Realistically, this would need
                # more specific parsing based on the API's response structure.
                # For now, we'll assume a simple structure or just log the data.
                logger.info(f"API data received (first 200 chars): {str(data)[:200]}")
                # Example: if API returns a list of articles with 'title' and 'url'
                if isinstance(data, list):
                    for item in data:
                        title = item.get("title", "No Title")
                        url = item.get("url", "#")
                        snippet = item.get("description", item.get("snippet", None))
                        await crud.create_article_in_main_backend(
                            podcast_id=podcast_id,
                            source_block_id=source_block_id,
                            url=url,
                            title=title,
                            snippet=snippet
                        )
                        logger.info(f"Ingested API article: {title}")

    except Exception as e:
        logger.error(f"Error ingesting API from {rule.url}: {e}", exc_info=True)
    return articles

async def ingest_scrape(rule: schemas.IngestionRule, podcast_id: str, source_block_id: str):
    logger.info(f"Ingesting scrape from: {rule.url}")
    articles = []
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(rule.url) as response:
                response.raise_for_status()
                html_content = await response.text()
                soup = BeautifulSoup(html_content, 'lxml')

                # This is a very basic scraping example. The extraction_schema
                # would be used here for more complex, declarative scraping.
                # For now, we'll just try to find some common article elements.
                
                # Example: Find all h2 tags that might be article titles
                for h2 in soup.find_all('h2'):
                    title = h2.get_text(strip=True)
                    link = h2.find('a', href=True)
                    url = link['href'] if link else rule.url # Fallback to page URL
                    
                    # In a real scenario, extraction_schema would guide this much more precisely
                    # For simplicity, we'll just create a placeholder article
                    await crud.create_article_in_main_backend(
                        podcast_id=podcast_id,
                        source_block_id=source_block_id,
                        url=url,
                        title=title,
                        snippet=None # No snippet from this simple example
                    )
                    logger.info(f"Ingested scraped article: {title}")

    except Exception as e:
        logger.error(f"Error ingesting scrape from {rule.url}: {e}", exc_info=True)
    return articles


@app.post("/ingest/", status_code=202)
async def ingest_content(request: schemas.IngestionRequest):
    logger.info(f"Received ingestion request for podcast {request.podcast_id} with block: {request.block_definition.description}")
    
    # In a real-world scenario, this would likely dispatch to a task queue
    # (e.g., Celery, Redis Queue) to run in the background.
    # For now, we'll run it directly.
    
    tasks = []
    for rule in request.block_definition.ingestion_rules:
        if rule.type == "rss":
            tasks.append(ingest_rss(rule, request.podcast_id, request.block_definition.description)) # Using description as source_block_id for now
        elif rule.type == "api":
            tasks.append(ingest_api(rule, request.podcast_id, request.block_definition.description))
        elif rule.type == "scrape":
            tasks.append(ingest_scrape(rule, request.podcast_id, request.block_definition.description))
        else:
            logger.warning(f"Unknown ingestion rule type: {rule.type}")

    # Run all ingestion tasks concurrently
    import asyncio
    await asyncio.gather(*tasks)

    logger.info(f"Finished processing ingestion request for podcast {request.podcast_id}")
    return {"message": "Ingestion request accepted and processing started.", "podcast_id": request.podcast_id}
