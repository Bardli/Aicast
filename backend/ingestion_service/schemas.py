from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Any
import uuid
from datetime import datetime

# Pydantic models for the 'ingestion_rules' array within the Block definition
class IngestionRule(BaseModel):
    type: Literal["rss", "api", "scrape"]
    url: str
    extraction_schema: Optional[Dict[str, Any]] = None

# Pydantic model for the 'definition' JSONB field in the Block table
class BlockDefinition(BaseModel):
    description: str
    ingestion_rules: List[IngestionRule]

# Schema for the ingestion request
class IngestionRequest(BaseModel):
    podcast_id: str
    block_definition: BlockDefinition

# Schema for the Article produced by the ingestion service
class ArticleCreate(BaseModel):
    podcast_id: str
    source_block_id: str # This will be the block_id from the original request
    url: str
    title: str
    snippet: Optional[str] = None
