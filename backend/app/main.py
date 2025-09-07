import logging
from logging.handlers import RotatingFileHandler
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid

from . import crud, models, schemas
from .database import SessionLocal, engine, get_db

# --- Logging Configuration ---
log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log_file = "backend_app.log"

# Use RotatingFileHandler for log rotation
file_handler = RotatingFileHandler(log_file, maxBytes=1024 * 1024 * 5, backupCount=2) # 5MB per file
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.INFO)

# Get root logger and add handler
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)

# --- Database and App Initialization ---
logger.info("Creating database tables...")
try:
    models.Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully.")
except Exception as e:
    logger.error(f"Error creating database tables: {e}", exc_info=True)
    # We might want to exit if the DB can't be set up.
    # For now, just log the error.
    raise e

app = FastAPI(
    title="AI-Powered Audio News Platform API",
    description="API for the AI-Powered Audio News Platform",
    version="0.1.0",
)

@app.on_event("startup")
async def startup_event():
    logger.info("--- Application startup ---")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("--- Application shutdown ---")


@app.get("/")
def read_root():
    return {"message": "Welcome to the AI-Powered Audio News Platform API"}

# --- Block Endpoints ---

@app.post("/blocks/", response_model=schemas.Block, tags=["Blocks"])
def create_block(block: schemas.BlockCreate, db: Session = Depends(get_db)):
    """
    Create a new Block.
    """
    logger.info(f"Received request to create block with name: {block.name}")
    try:
        created_block = crud.create_block(db=db, block=block)
        logger.info(f"Successfully created block with ID: {created_block.block_id}")
        return created_block
    except Exception as e:
        logger.error(f"Error creating block: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error while creating block.")


@app.get("/blocks/", response_model=List[schemas.Block], tags=["Blocks"])
def read_blocks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve all Blocks with pagination.
    """
    logger.info(f"Received request to read blocks with skip={skip}, limit={limit}")
    try:
        blocks = crud.get_blocks(db, skip=skip, limit=limit)
        logger.info(f"Found {len(blocks)} blocks.")
        return blocks
    except Exception as e:
        logger.error(f"Error reading blocks: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error while reading blocks.")


@app.get("/blocks/{block_id}", response_model=schemas.Block, tags=["Blocks"])
def read_block(block_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Retrieve a single Block by its ID.
    """
    logger.info(f"Received request to read block with ID: {block_id}")
    try:
        db_block = crud.get_block(db, block_id=block_id)
        if db_block is None:
            logger.warning(f"Block with ID {block_id} not found.")
            raise HTTPException(status_code=404, detail="Block not found")
        logger.info(f"Successfully found block with ID: {block_id}")
        return db_block
    except Exception as e:
        logger.error(f"Error reading block with ID {block_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error while reading block.")


# --- User Endpoints ---

@app.post("/users/", response_model=schemas.User, tags=["Users"])
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Create a new User.
    """
    logger.info(f"Received request to create user with email: {user.email}")
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        logger.warning(f"User with email {user.email} already exists.")
        raise HTTPException(status_code=400, detail="Email already registered")
    try:
        created_user = crud.create_user(db=db, user=user)
        logger.info(f"Successfully created user with ID: {created_user.user_id}")
        return created_user
    except Exception as e:
        logger.error(f"Error creating user: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error while creating user.")


@app.get("/users/", response_model=List[schemas.User], tags=["Users"])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve all Users with pagination.
    """
    logger.info(f"Received request to read users with skip={skip}, limit={limit}")
    try:
        users = crud.get_users(db, skip=skip, limit=limit)
        logger.info(f"Found {len(users)} users.")
        return users
    except Exception as e:
        logger.error(f"Error reading users: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error while reading users.")


@app.get("/users/{user_id}", response_model=schemas.User, tags=["Users"])
def read_user(user_id: str, db: Session = Depends(get_db)):
    """
    Retrieve a single User by their ID.
    """
    logger.info(f"Received request to read user with ID: {user_id}")
    try:
        db_user = crud.get_user(db, user_id=user_id)
        if db_user is None:
            logger.warning(f"User with ID {user_id} not found.")
            raise HTTPException(status_code=404, detail="User not found")
        logger.info(f"Successfully found user with ID: {user_id}")
        return db_user
    except Exception as e:
        logger.error(f"Error reading user with ID {user_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error while reading user.")


# --- Podcast Endpoints ---

@app.post("/podcasts/", response_model=schemas.Podcast, tags=["Podcasts"])
def create_podcast(podcast: schemas.PodcastCreate, db: Session = Depends(get_db)):
    """
    Create a new Podcast.
    """
    logger.info(f"Received request to create podcast for user: {podcast.user_id}")
    try:
        created_podcast = crud.create_podcast(db=db, podcast=podcast)
        logger.info(f"Successfully created podcast with ID: {created_podcast.podcast_id}")
        return created_podcast
    except Exception as e:
        logger.error(f"Error creating podcast: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error while creating podcast.")


@app.get("/podcasts/by_user/{user_id}", response_model=List[schemas.Podcast], tags=["Podcasts"])
def read_podcasts_by_user(user_id: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve all Podcasts for a specific User with pagination.
    """
    logger.info(f"Received request to read podcasts for user {user_id} with skip={skip}, limit={limit}")
    try:
        podcasts = crud.get_podcasts_by_user(db, user_id=user_id, skip=skip, limit=limit)
        logger.info(f"Found {len(podcasts)} podcasts for user {user_id}.")
        return podcasts
    except Exception as e:
        logger.error(f"Error reading podcasts for user {user_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error while reading podcasts.")


@app.get("/podcasts/{podcast_id}", response_model=schemas.Podcast, tags=["Podcasts"])
def read_podcast(podcast_id: str, db: Session = Depends(get_db)):
    """
    Retrieve a single Podcast by its ID.
    """
    logger.info(f"Received request to read podcast with ID: {podcast_id}")
    try:
        db_podcast = crud.get_podcast(db, podcast_id=podcast_id)
        if db_podcast is None:
            logger.warning(f"Podcast with ID {podcast_id} not found.")
            raise HTTPException(status_code=404, detail="Podcast not found")
        logger.info(f"Successfully found podcast with ID: {podcast_id}")
        return db_podcast
    except Exception as e:
        logger.error(f"Error reading podcast with ID {podcast_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error while reading podcast.")


@app.put("/podcasts/{podcast_id}/status", response_model=schemas.Podcast, tags=["Podcasts"])
def update_podcast_status(podcast_id: str, status: str, db: Session = Depends(get_db)):
    """
    Update the status of a Podcast.
    """
    logger.info(f"Received request to update status for podcast {podcast_id} to {status}")
    try:
        updated_podcast = crud.update_podcast_status(db, podcast_id=podcast_id, status=status)
        if updated_podcast is None:
            logger.warning(f"Podcast with ID {podcast_id} not found for status update.")
            raise HTTPException(status_code=404, detail="Podcast not found")
        logger.info(f"Successfully updated status for podcast {podcast_id} to {status}.")
        return updated_podcast
    except Exception as e:
        logger.error(f"Error updating status for podcast {podcast_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error while updating podcast status.")


@app.put("/podcasts/{podcast_id}/complete", response_model=schemas.Podcast, tags=["Podcasts"])
def complete_podcast(podcast_id: str, final_script: str, audio_url: str, db: Session = Depends(get_db)):
    """
    Mark a Podcast as completed, providing the final script and audio URL.
    """
    logger.info(f"Received request to complete podcast {podcast_id}")
    try:
        completed_podcast = crud.update_podcast_script_and_audio(db, podcast_id=podcast_id, final_script=final_script, audio_url=audio_url)
        if completed_podcast is None:
            logger.warning(f"Podcast with ID {podcast_id} not found for completion.")
            raise HTTPException(status_code=404, detail="Podcast not found")
        logger.info(f"Successfully completed podcast {podcast_id}.")
        return completed_podcast
    except Exception as e:
        logger.error(f"Error completing podcast {podcast_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error while completing podcast.")


# --- PodcastBlock Endpoints ---

@app.post("/podcast_blocks/", response_model=schemas.PodcastBlock, tags=["Podcast Blocks"])
def create_podcast_block(podcast_block: schemas.PodcastBlockCreate, db: Session = Depends(get_db)):
    """
    Create a new PodcastBlock (link between a Podcast and a Block).
    """
    logger.info(f"Received request to create podcast block for podcast {podcast_block.podcast_id} and block {podcast_block.block_id}")
    try:
        created_podcast_block = crud.create_podcast_block(db=db, podcast_block=podcast_block)
        logger.info(f"Successfully created podcast block with ID: {created_podcast_block.id}")
        return created_podcast_block
    except Exception as e:
        logger.error(f"Error creating podcast block: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error while creating podcast block.")


@app.get("/podcast_blocks/by_podcast/{podcast_id}", response_model=List[schemas.PodcastBlock], tags=["Podcast Blocks"])
def read_podcast_blocks_by_podcast(podcast_id: str, db: Session = Depends(get_db)):
    """
    Retrieve all PodcastBlocks for a specific Podcast, ordered by sequence.
    """
    logger.info(f"Received request to read podcast blocks for podcast: {podcast_id}")
    try:
        podcast_blocks = crud.get_podcast_blocks_by_podcast(db, podcast_id=podcast_id)
        logger.info(f"Found {len(podcast_blocks)} podcast blocks for podcast {podcast_id}.")
        return podcast_blocks
    except Exception as e:
        logger.error(f"Error reading podcast blocks for podcast {podcast_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error while reading podcast blocks.")


# --- Article Endpoints ---

@app.post("/articles/", response_model=schemas.Article, tags=["Articles"])
def create_article(article: schemas.ArticleCreate, db: Session = Depends(get_db)):
    """
    Create a new Article.
    """
    logger.info(f"Received request to create article for podcast {article.podcast_id}")
    try:
        created_article = crud.create_article(db=db, article=article)
        logger.info(f"Successfully created article with ID: {created_article.article_id}")
        return created_article
    except Exception as e:
        logger.error(f"Error creating article: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error while creating article.")


@app.get("/articles/by_podcast/{podcast_id}", response_model=List[schemas.Article], tags=["Articles"])
def read_articles_by_podcast(podcast_id: str, db: Session = Depends(get_db)):
    """
    Retrieve all Articles for a specific Podcast.
    """
    logger.info(f"Received request to read articles for podcast: {podcast_id}")
    try:
        articles = crud.get_articles_by_podcast(db, podcast_id=podcast_id)
        logger.info(f"Found {len(articles)} articles for podcast {podcast_id}.")
        return articles
    except Exception as e:
        logger.error(f"Error reading articles for podcast {podcast_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error while reading articles.")
