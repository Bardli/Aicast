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
