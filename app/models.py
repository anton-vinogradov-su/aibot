"""Database models"""
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import DeclarativeBase, relationship, sessionmaker

from app.config import settings


class Base(DeclarativeBase):
    """Base class for all models"""
    pass


class NewsItem(Base):
    """News item model"""
    __tablename__ = "news_items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    url = Column(String(1000), nullable=False, unique=True, index=True)
    summary = Column(Text)
    source = Column(String(100), nullable=False, index=True)
    published_at = Column(DateTime, nullable=False, index=True)
    raw_text = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    posts = relationship("Post", back_populates="news_item")

    def __repr__(self):
        return f"<NewsItem(id={self.id}, title='{self.title[:50]}...')>"


class Post(Base):
    """Generated post model"""
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    news_id = Column(Integer, ForeignKey("news_items.id"), nullable=False)
    generated_text = Column(Text, nullable=False)
    published_at = Column(DateTime, index=True)
    status = Column(String(50), default="pending", index=True)  # pending, published, failed
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    news_item = relationship("NewsItem", back_populates="posts")

    def __repr__(self):
        return f"<Post(id={self.id}, status='{self.status}')>"


class Source(Base):
    """News source model"""
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(50), nullable=False)  # website, telegram
    name = Column(String(100), nullable=False, unique=True)
    url = Column(String(1000), nullable=False)
    enabled = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Source(id={self.id}, name='{self.name}')>"


class Keyword(Base):
    """Keyword for filtering model"""
    __tablename__ = "keywords"

    id = Column(Integer, primary_key=True, index=True)
    word = Column(String(100), nullable=False, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Keyword(id={self.id}, word='{self.word}')>"


# Database setup
engine = create_engine(settings.database_url, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
