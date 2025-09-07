from sqlalchemy.orm import Session
import uuid
from . import models, schemas

def get_block(db: Session, block_id: uuid.UUID):
    return db.query(models.Block).filter(models.Block.block_id == block_id).first()

def get_blocks(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Block).offset(skip).limit(limit).all()

def create_block(db: Session, block: schemas.BlockCreate):
    # Pydantic's model_dump() is used to convert the definition model to a dict for JSONB storage.
    db_block = models.Block(
        name=block.name,
        is_official=block.is_official,
        owner_id=block.owner_id,
        definition=block.definition.model_dump()
    )
    db.add(db_block)
    db.commit()
    db.refresh(db_block)
    return db_block


# --- User CRUD ---
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user(db: Session, user_id: str):
    return db.query(models.User).filter(models.User.user_id == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    # In a real application, you would hash the password here
    db_user = models.User(email=user.email, hashed_password=user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# --- Podcast CRUD ---
def get_podcast(db: Session, podcast_id: str):
    return db.query(models.Podcast).filter(models.Podcast.podcast_id == podcast_id).first()

def get_podcasts_by_user(db: Session, user_id: str, skip: int = 0, limit: int = 100):
    return db.query(models.Podcast).filter(models.Podcast.user_id == user_id).offset(skip).limit(limit).all()

def create_podcast(db: Session, podcast: schemas.PodcastCreate):
    db_podcast = models.Podcast(user_id=podcast.user_id, title=podcast.title, status=podcast.status)
    db.add(db_podcast)
    db.commit()
    db.refresh(db_podcast)
    return db_podcast

def update_podcast_status(db: Session, podcast_id: str, status: str):
    db_podcast = db.query(models.Podcast).filter(models.Podcast.podcast_id == podcast_id).first()
    if db_podcast:
        db_podcast.status = status
        db.commit()
        db.refresh(db_podcast)
    return db_podcast

def update_podcast_script_and_audio(db: Session, podcast_id: str, final_script: str, audio_url: str):
    db_podcast = db.query(models.Podcast).filter(models.Podcast.podcast_id == podcast_id).first()
    if db_podcast:
        db_podcast.final_script = final_script
        db_podcast.audio_url = audio_url
        db_podcast.status = "COMPLETED"
        db.commit()
        db.refresh(db_podcast)
    return db_podcast


# --- PodcastBlock CRUD ---
def create_podcast_block(db: Session, podcast_block: schemas.PodcastBlockCreate):
    db_podcast_block = models.PodcastBlock(
        podcast_id=podcast_block.podcast_id,
        block_id=podcast_block.block_id,
        sequence_order=podcast_block.sequence_order
    )
    db.add(db_podcast_block)
    db.commit()
    db.refresh(db_podcast_block)
    return db_podcast_block

def get_podcast_blocks_by_podcast(db: Session, podcast_id: str):
    return db.query(models.PodcastBlock).filter(models.PodcastBlock.podcast_id == podcast_id).order_by(models.PodcastBlock.sequence_order).all()


# --- Article CRUD ---
def create_article(db: Session, article: schemas.ArticleCreate):
    db_article = models.Article(
        podcast_id=article.podcast_id,
        source_block_id=article.source_block_id,
        url=article.url,
        title=article.title,
        snippet=article.snippet
    )
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    return db_article

def get_articles_by_podcast(db: Session, podcast_id: str):
    return db.query(models.Article).filter(models.Article.podcast_id == podcast_id).all()
