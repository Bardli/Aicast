from fastapi import FastAPI, HTTPException
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv
import os
from typing import List, Dict, Any
import openai

from . import schemas, crud

# Load environment variables from .env file
load_dotenv()

# --- Logging Configuration ---
log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log_file = "llm_orchestration_service.log"

# Use RotatingFileHandler for log rotation
file_handler = RotatingFileHandler(log_file, maxBytes=1024 * 1024 * 5, backupCount=2) # 5MB per file
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.INFO)

# Get root logger and add handler
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)

app = FastAPI(
    title="LLM Orchestration Service",
    description="Service for synthesizing narratives using LLMs.",
    version="0.1.0",
)

# Initialize OpenAI client
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    logger.error("OPENAI_API_KEY not found in environment variables. LLM calls will fail.")
    # In a real app, you might want to raise an exception or handle this more gracefully
    # For now, we'll proceed but expect errors if key is missing.

client = openai.OpenAI(api_key=openai_api_key)

@app.on_event("startup")
async def startup_event():
    logger.info("--- LLM Orchestration Service startup ---")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("--- LLM Orchestration Service shutdown ---")

@app.get("/")
def read_root():
    return {"message": "LLM Orchestration Service is running"}


# --- LLM Orchestration Logic ---

async def synthesize_articles(articles: List[schemas.Article]) -> Dict[str, Any]:
    """
    Stage 1: The Synthesizer (Parallel Processing)
    Processes a list of articles to extract summaries, key points, sentiment, and narrative angle.
    """
    synthesized_outputs = []
    for article in articles:
        prompt = f"""
        You are a specialist news analysis AI. Your task is to process the following article related to the topic: "{article.source_block_id}".
        Your response must be based ONLY on the information contained within the provided article. Do not add external knowledge or opinions.

        ARTICLE:
        ---
        Title: {article.title}
        URL: {article.url}
        Snippet: {article.snippet if article.snippet else 'N/A'}
        ---

        Based exclusively on the article above, provide your analysis in a structured JSON format with the following keys:
        - "summary": A concise, neutral summary of the main news events and developments (2-3 sentences).
        - "key_points": A bulleted list of the 3 most significant facts, figures, or direct quotes.
        - "sentiment": A single word describing the overall tone of the reporting (e.g., "Bullish", "Bearish", "Neutral", "Volatile", "Developing").
        - "narrative_angle": Suggest a single, compelling narrative angle for presenting this news segment in a podcast (e.g., "A story of unexpected corporate turnaround," "A cautionary tale for tech investors," "The political fallout from a new policy").
        """
        try:
            response = client.chat.completions.create(
                model="gpt-4o", # Using a capable model
                response_format={ "type": "json_object" },
                messages=[
                    {"role": "system", "content": "You are a helpful assistant designed to output JSON."}, # Added for JSON output
                    {"role": "user", "content": prompt}
                ]
            )
            synthesized_outputs.append(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"Error during synthesis for article {article.article_id}: {e}", exc_info=True)
            synthesized_outputs.append(None) # Append None to maintain order
    return synthesized_outputs

async def weave_narrative(synthesized_outputs: List[Dict[str, Any]]) -> str:
    """
    Stage 2: The Weaver (Sequential Synthesis)
    Takes synthesized outputs and weaves them into a coherent podcast script.
    """
    # Filter out any None values from failed syntheses
    valid_outputs = [output for output in synthesized_outputs if output is not None]
    if not valid_outputs:
        return "No content available to generate podcast script."

    # Convert list of dicts to JSON string for the prompt
    import json
    synthesized_json = json.dumps(valid_outputs, indent=2)

    prompt = f"""
    You are a world-class podcast host named 'Alex'. Your tone is authoritative yet engaging, clear, and professional. Your task is to write the complete, ready-to-read script for today's personalized news briefing.

    Follow these steps meticulously to construct the script:
    1.  **Overall Introduction**: Begin with a brief, welcoming introduction. Look at the 'narrative_angle' of the first few segments and craft an opening that teases the main themes of today's briefing.
    2.  **Segment Weaving**: Proceed through each news segment provided below in the exact order they are given. For each segment, use its 'narrative_angle' and 'summary' to introduce the topic smoothly. Then, naturally weave in the 'key_points' as the core details of the segment.
    3.  **Critical Transitions**: This is the most important part of your task. You must create smooth, logical, and conversational transitions between each news segment. Acknowledge the shift in topic, geography, or sentiment. For example: "Now, shifting gears from the turbulence in the financial markets, let's turn our attention to some groundbreaking developments in the world of biotechnology..." or "That policy decision in Europe has significant implications, which brings us to our next story on international trade..."
    4.  **Source Attribution**: Where it feels natural, casually attribute key information to its source to build credibility. For example, "...according to a report from Reuters..."
    5.  **Concluding Summary**: After the final segment, provide a brief concluding summary that recaps the main stories and end with a warm, professional sign-off.

    Here is the sequence of news segments for your script, provided as a JSON array:
    ---
    {synthesized_json}
    ---

    Now, please write the complete podcast script for 'Alex', ready for broadcast.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o", # Using a capable model
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error during narrative weaving: {e}", exc_info=True)
        return "Error generating script."


@app.post("/orchestrate/", response_model=schemas.LLMOrchestrationResponse, status_code=202)
async def orchestrate_llm(request: schemas.LLMOrchestrationRequest):
    logger.info(f"Received LLM orchestration request for podcast {request.podcast_id}")
    
    # Stage 1: Synthesize articles
    synthesized_outputs = await synthesize_articles(request.articles)
    
    # Stage 2: Weave narrative
    final_script = await weave_narrative(synthesized_outputs)
    
    # Update main backend with the final script
    try:
        await crud.update_podcast_script_in_main_backend(
            podcast_id=request.podcast_id,
            final_script=final_script
        )
        logger.info(f"Successfully updated podcast {request.podcast_id} with final script.")
    except Exception as e:
        logger.error(f"Error updating main backend for podcast {request.podcast_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to update main backend with script.")

    return schemas.LLMOrchestrationResponse(
        podcast_id=request.podcast_id,
        final_script=final_script
    )
