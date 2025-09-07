import sqlalchemy
from sqlalchemy import (
    create_engine,
    Column,
    String,
    Boolean,
    ForeignKey,
    Integer,
    Text,
    BigInteger,
    TIMESTAMP,
    JSON,
)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func
import uuid

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    user_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
    blocks = relationship("Block", back_populates="owner")
    podcasts = relationship("Podcast", back_populates="user")


class Block(Base):
    __tablename__ = "blocks"
    block_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_id = Column(String(36), ForeignKey("users.user_id"), nullable=True)
    is_official = Column(Boolean, nullable=False, default=False, index=True)
    name = Column(String(255), nullable=False)
    definition = Column(JSON, nullable=False)

    owner = relationship("User", back_populates="blocks")
    articles = relationship("Article", back_populates="source_block")


class Podcast(Base):
    __tablename__ = "podcasts"
    podcast_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=True)
    status = Column(
        String(50), nullable=False, default="PENDING", index=True
    )
    final_script = Column(Text, nullable=True)
    audio_url = Column(String(1024), nullable=True)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )

    user = relationship("User", back_populates="podcasts")
    articles = relationship("Article", back_populates="podcast")
    podcast_blocks = relationship("PodcastBlock", back_populates="podcast")


class PodcastBlock(Base):
    __tablename__ = "podcast_blocks"
    id = Column(BigInteger, primary_key=True)
    podcast_id = Column(
        String(36), ForeignKey("podcasts.podcast_id", ondelete="CASCADE"), nullable=False
    )
    block_id = Column(
        String(36), ForeignKey("blocks.block_id", ondelete="CASCADE"), nullable=False
    )
    sequence_order = Column(Integer, nullable=False)

    podcast = relationship("Podcast", back_populates="podcast_blocks")
    block = relationship("Block")


class Article(Base):
    __tablename__ = "articles"
    article_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    podcast_id = Column(
        String(36), ForeignKey("podcasts.podcast_id", ondelete="CASCADE"), nullable=False, index=True
    )
    source_block_id = Column(
        String(36), ForeignKey("blocks.block_id", ondelete="SET NULL"), nullable=False
    )
    url = Column(String(2048), nullable=False)
    title = Column(Text, nullable=False)
    snippet = Column(Text, nullable=True)
    retrieved_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )

    podcast = relationship("Podcast", back_populates="articles")
    source_block = relationship("Block", back_populates="articles")
