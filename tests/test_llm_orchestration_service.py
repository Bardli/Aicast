import pytest
import httpx # Keep httpx for potential external calls if needed, but not for app testing
import asyncio
import os
from dotenv import load_dotenv
from starlette.testclient import TestClient # Import TestClient
import pytest_asyncio

# Import the FastAPI app directly
from backend.llm_orchestration_service.main import app

# Load environment variables from .env file for tests
load_dotenv()

@pytest_asyncio.fixture(scope="module")
async def llm_orchestration_client():
    """
    Fixture to provide a TestClient for testing the FastAPI app directly.
    """
    with TestClient(app) as client: # TestClient is synchronous, no async with needed here
        yield client

@pytest.mark.asyncio
async def test_llm_orchestration_service_startup(llm_orchestration_client):
    """
    Test that the LLM Orchestration Service's root endpoint is accessible.
    """
    response = llm_orchestration_client.get("/") # TestClient methods are synchronous
    assert response.status_code == 200
    assert response.json() == {"message": "LLM Orchestration Service is running"}

@pytest.mark.asyncio
async def test_orchestrate_endpoint_failure(llm_orchestration_client):
    """
    Test the /orchestrate/ endpoint with a sample request.
    This test is expected to fail initially due to missing API key or LLM issues.
    The goal is to capture the error output.
    """
    sample_request = {
        "podcast_id": "test-podcast-id",
        "articles": [
            {
                "article_id": "test-article-id-1",
                "podcast_id": "test-podcast-id",
                "source_block_id": "Test Source",
                "url": "http://example.com/article1",
                "title": "Test Article 1",
                "snippet": "This is a snippet for test article 1.",
                "retrieved_at": "2025-01-01T12:00:00"
            }
        ]
    }
    
    response = llm_orchestration_client.post("/orchestrate/", json=sample_request) # TestClient methods are synchronous
    
    # This assertion is expected to fail initially, but will capture the error
    assert response.status_code == 202 # Expect 202 Accepted if request is valid
    assert "final_script" in response.json()