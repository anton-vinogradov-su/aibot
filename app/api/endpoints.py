"""API endpoints"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import schemas
from app.models import Keyword, NewsItem, Post, Source, get_db

router = APIRouter()


# Sources endpoints
@router.get("/sources", response_model=List[schemas.SourceResponse])
def get_sources(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all sources"""
    sources = db.query(Source).offset(skip).limit(limit).all()
    return sources


@router.post("/sources", response_model=schemas.SourceResponse, status_code=201)
def create_source(source: schemas.SourceCreate, db: Session = Depends(get_db)):
    """Create new source"""
    db_source = Source(**source.model_dump())
    db.add(db_source)
    db.commit()
    db.refresh(db_source)
    return db_source


@router.patch("/sources/{source_id}", response_model=schemas.SourceResponse)
def update_source(
    source_id: int,
    source_update: schemas.SourceUpdate,
    db: Session = Depends(get_db)
):
    """Update source"""
    db_source = db.query(Source).filter(Source.id == source_id).first()
    if not db_source:
        raise HTTPException(status_code=404, detail="Source not found")

    update_data = source_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_source, key, value)

    db.commit()
    db.refresh(db_source)
    return db_source


@router.delete("/sources/{source_id}", status_code=204)
def delete_source(source_id: int, db: Session = Depends(get_db)):
    """Delete source"""
    db_source = db.query(Source).filter(Source.id == source_id).first()
    if not db_source:
        raise HTTPException(status_code=404, detail="Source not found")

    db.delete(db_source)
    db.commit()
    return None


# Keywords endpoints
@router.get("/keywords", response_model=List[schemas.KeywordResponse])
def get_keywords(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all keywords"""
    keywords = db.query(Keyword).offset(skip).limit(limit).all()
    return keywords


@router.post("/keywords", response_model=schemas.KeywordResponse, status_code=201)
def create_keyword(keyword: schemas.KeywordCreate, db: Session = Depends(get_db)):
    """Create new keyword"""
    db_keyword = Keyword(**keyword.model_dump())
    db.add(db_keyword)
    db.commit()
    db.refresh(db_keyword)
    return db_keyword


@router.delete("/keywords/{keyword_id}", status_code=204)
def delete_keyword(keyword_id: int, db: Session = Depends(get_db)):
    """Delete keyword"""
    db_keyword = db.query(Keyword).filter(Keyword.id == keyword_id).first()
    if not db_keyword:
        raise HTTPException(status_code=404, detail="Keyword not found")

    db.delete(db_keyword)
    db.commit()
    return None


# News endpoints
@router.get("/news", response_model=List[schemas.NewsItemResponse])
def get_news(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """Get news items"""
    news = db.query(NewsItem).order_by(NewsItem.id.desc()).offset(skip).limit(limit).all()
    return news


@router.get("/news/{news_id}", response_model=schemas.NewsItemResponse)
def get_news_item(news_id: int, db: Session = Depends(get_db)):
    """Get single news item"""
    news = db.query(NewsItem).filter(NewsItem.id == news_id).first()
    if not news:
        raise HTTPException(status_code=404, detail="News item not found")
    return news


# Posts endpoints
@router.get("/posts", response_model=List[schemas.PostResponse])
def get_posts(
    status: str = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get posts"""
    query = db.query(Post)
    if status:
        query = query.filter(Post.status == status)
    posts = query.order_by(Post.id.desc()).offset(skip).limit(limit).all()
    return posts


@router.get("/posts/{post_id}", response_model=schemas.PostResponse)
def get_post(post_id: int, db: Session = Depends(get_db)):
    """Get single post"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


# Statistics endpoint
@router.get("/stats", response_model=schemas.StatsResponse)
def get_stats(db: Session = Depends(get_db)):
    """Get statistics"""
    total_news = db.query(NewsItem).count()
    total_posts = db.query(Post).count()
    published_posts = db.query(Post).filter(Post.status == "published").count()
    pending_posts = db.query(Post).filter(Post.status == "pending").count()
    failed_posts = db.query(Post).filter(Post.status == "failed").count()
    total_sources = db.query(Source).count()
    active_sources = db.query(Source).filter(Source.enabled == True).count()

    return schemas.StatsResponse(
        total_news=total_news,
        total_posts=total_posts,
        published_posts=published_posts,
        pending_posts=pending_posts,
        failed_posts=failed_posts,
        total_sources=total_sources,
        active_sources=active_sources
    )
