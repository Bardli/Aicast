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
