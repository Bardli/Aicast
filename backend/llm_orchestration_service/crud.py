import httpx
from typing import Optional

MAIN_BACKEND_API_URL = "http://127.0.0.1:8000" # This should be configurable

async def update_podcast_script_in_main_backend(
    podcast_id: str,
    final_script: str,
    audio_url: Optional[str] = None # Audio URL will be added by Audio Generation Service
):
    # The main backend's /podcasts/{podcast_id}/complete endpoint expects final_script and audio_url
    # For now, we'll just update the script and set audio_url to a placeholder or None
    # The Audio Generation Service will later update this with the actual audio URL
    
    # Note: The main backend's update_podcast_script_and_audio expects final_script and audio_url
    # We'll call that endpoint.
    
    # The main backend's endpoint is PUT /podcasts/{podcast_id}/complete
    # It expects final_script and audio_url as query parameters.
    
    params = {
        "final_script": final_script,
        "audio_url": audio_url if audio_url else "" # Send empty string if None
    }

    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{MAIN_BACKEND_API_URL}/podcasts/{podcast_id}/complete",
            params=params
        )
        response.raise_for_status() # Raise an exception for 4xx/5xx responses
        return response.json()
