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

# Base Pydantic model for a Block
class BlockBase(BaseModel):
    name: str
    is_official: bool = False
    definition: BlockDefinition

# Pydantic model for creating a new Block (input)
class BlockCreate(BlockBase):
    owner_id: Optional[str] = None

# Pydantic model for reading a Block from the database (output)
class Block(BlockBase):
    block_id: str
    owner_id: Optional[str] = None

    class Config:
        from_attributes = True


# --- User Schemas ---
class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    user_id: str

    class Config:
        from_attributes = True


# --- Podcast Schemas ---
class PodcastBase(BaseModel):
    title: Optional[str] = None
    status: str = "PENDING"
    final_script: Optional[str] = None
    audio_url: Optional[str] = None

class PodcastCreate(PodcastBase):
    user_id: str

class Podcast(PodcastBase):
    podcast_id: str
    user_id: str
    title: Optional[str] = None
    status: str
    final_script: Optional[str] = None
    audio_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# --- PodcastBlock Schemas ---
class PodcastBlockBase(BaseModel):
    podcast_id: str
    block_id: str
    sequence_order: int

class PodcastBlockCreate(PodcastBlockBase):
    pass

class PodcastBlock(PodcastBlockBase):
    id: int

    class Config:
        from_attributes = True


# --- Article Schemas ---
class ArticleBase(BaseModel):
    podcast_id: str
    source_block_id: str
    url: str
    title: str
    snippet: Optional[str] = None

class ArticleCreate(ArticleBase):
    pass

class Article(ArticleBase):
    article_id: str
    retrieved_at: datetime

    class Config:
        from_attributes = True