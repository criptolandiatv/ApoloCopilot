"""Forum routes"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from database import get_db
from models.user import User
from models.forum import ForumCategory, ForumThread, ForumPost
from utils.security import get_verified_user

router = APIRouter(prefix="/api/forum", tags=["Forum"])


class CategoryResponse(BaseModel):
    id: int
    name: str
    description: str | None
    slug: str
    icon: str | None

    class Config:
        from_attributes = True


class ThreadCreate(BaseModel):
    title: str
    content: str
    category_id: int


class ThreadResponse(BaseModel):
    id: int
    title: str
    content: str
    author_id: int
    views: int
    is_pinned: bool
    is_locked: bool
    created_at: str
    updated_at: str | None

    class Config:
        from_attributes = True


class PostCreate(BaseModel):
    content: str


class PostResponse(BaseModel):
    id: int
    content: str
    author_id: int
    created_at: str
    is_edited: bool

    class Config:
        from_attributes = True


@router.get("/categories", response_model=List[CategoryResponse])
async def get_categories(db: Session = Depends(get_db)):
    """Get all forum categories"""
    categories = db.query(ForumCategory).order_by(ForumCategory.order).all()
    return categories


@router.post("/categories")
async def create_category(
    name: str,
    description: str,
    slug: str,
    current_user: User = Depends(get_verified_user),
    db: Session = Depends(get_db)
):
    """Create a forum category (admin only - simplified)"""
    category = ForumCategory(
        name=name,
        description=description,
        slug=slug
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    return category


@router.get("/threads", response_model=List[ThreadResponse])
async def get_threads(
    category_id: Optional[int] = None,
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db)
):
    """Get forum threads"""
    query = db.query(ForumThread)

    if category_id:
        query = query.filter(ForumThread.category_id == category_id)

    threads = query.order_by(
        ForumThread.is_pinned.desc(),
        ForumThread.created_at.desc()
    ).limit(limit).all()

    return threads


@router.post("/threads", response_model=ThreadResponse)
async def create_thread(
    data: ThreadCreate,
    current_user: User = Depends(get_verified_user),
    db: Session = Depends(get_db)
):
    """Create a new forum thread"""
    # Verify category exists
    category = db.query(ForumCategory).filter(
        ForumCategory.id == data.category_id
    ).first()

    if not category:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")

    thread = ForumThread(
        category_id=data.category_id,
        author_id=current_user.id,
        title=data.title,
        content=data.content
    )

    db.add(thread)
    db.commit()
    db.refresh(thread)

    return thread


@router.get("/threads/{thread_id}", response_model=ThreadResponse)
async def get_thread(
    thread_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific thread"""
    thread = db.query(ForumThread).filter(ForumThread.id == thread_id).first()

    if not thread:
        raise HTTPException(status_code=404, detail="Thread não encontrada")

    # Increment views
    thread.views += 1
    db.commit()

    return thread


@router.get("/threads/{thread_id}/posts", response_model=List[PostResponse])
async def get_thread_posts(
    thread_id: int,
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db)
):
    """Get posts in a thread"""
    posts = db.query(ForumPost).filter(
        ForumPost.thread_id == thread_id
    ).order_by(ForumPost.created_at).limit(limit).all()

    return posts


@router.post("/threads/{thread_id}/posts", response_model=PostResponse)
async def create_post(
    thread_id: int,
    data: PostCreate,
    current_user: User = Depends(get_verified_user),
    db: Session = Depends(get_db)
):
    """Create a post in a thread"""
    # Verify thread exists and is not locked
    thread = db.query(ForumThread).filter(ForumThread.id == thread_id).first()

    if not thread:
        raise HTTPException(status_code=404, detail="Thread não encontrada")

    if thread.is_locked:
        raise HTTPException(status_code=403, detail="Thread está bloqueada")

    post = ForumPost(
        thread_id=thread_id,
        author_id=current_user.id,
        content=data.content
    )

    db.add(post)
    db.commit()
    db.refresh(post)

    return post
