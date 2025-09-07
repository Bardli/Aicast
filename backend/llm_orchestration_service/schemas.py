from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

# Schema for an Article received by the LLM Orchestration Service
# This should mirror the Article schema from the main backend
class Article(BaseModel):
    article_id: str
    podcast_id: str
    source_block_id: str
    url: str
    title: str
    snippet: Optional[str] = None
    retrieved_at: datetime

# Schema for the LLM Orchestration Request
class LLMOrchestrationRequest(BaseModel):
    podcast_id: str
    articles: List[Article]
    # Potentially add block_definitions here if needed for context in synthesis
    # For now, we'll assume articles contain enough info

# Schema for the LLM Orchestration Response
class LLMOrchestrationResponse(BaseModel):
    podcast_id: str
    final_script: str
