from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Any
import uuid

# Pydantic models for the 'ingestion_rules' array within the Block definition
class IngestionRule(BaseModel):
    type: Literal["rss", "api", "scrape"]
    url: str
    extraction_schema: Optional[Dict[str, Any]] = None

# Pydantic model for the 'definition' JSONB field in the Block table
class BlockDefinition(BaseModel):
    description: str
    ingestion_rules: List[IngestionRule]

# Base Pydantic model for a Block
class BlockBase(BaseModel):
    name: str
    is_official: bool = False
    definition: BlockDefinition

# Pydantic model for creating a new Block (input)
class BlockCreate(BlockBase):
    owner_id: Optional[uuid.UUID] = None

# Pydantic model for reading a Block from the database (output)
class Block(BlockBase):
    block_id: uuid.UUID
    owner_id: Optional[uuid.UUID] = None

    class Config:
        from_attributes = True
