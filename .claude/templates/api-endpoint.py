"""
${1:Resource} API Endpoint
Professional medical API with full validation and security
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime

from database import get_db
from models.user import User
from utils.security import get_verified_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/${2:resource-path}", tags=["${3:Resource}"])


# ============================================================================
# SCHEMAS
# ============================================================================

class ${1:Resource}Base(BaseModel):
    """Base schema for ${1:Resource}"""
    ${4:field_name}: ${5:str} = Field(..., description="${6:Field description}")

    @validator('${4:field_name}')
    def validate_${4:field_name}(cls, v):
        """Validate ${4:field_name}"""
        if not v or len(v) < 3:
            raise ValueError('${4:field_name} must be at least 3 characters')
        return v


class ${1:Resource}Create(${1:Resource}Base):
    """Schema for creating ${1:Resource}"""
    pass


class ${1:Resource}Update(BaseModel):
    """Schema for updating ${1:Resource}"""
    ${4:field_name}: Optional[${5:str}] = None


class ${1:Resource}Response(${1:Resource}Base):
    """Schema for ${1:Resource} response"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.get("/", response_model=List[${1:Resource}Response])
async def list_${2:resource}(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    current_user: User = Depends(get_verified_user),
    db: Session = Depends(get_db)
):
    """
    List all ${2:resource}

    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    - **search**: Optional search query
    """
    logger.info(f"User {current_user.id} listing ${2:resource}")

    query = db.query(${1:Resource})

    if search:
        query = query.filter(
            ${1:Resource}.${4:field_name}.ilike(f"%{search}%")
        )

    items = query.offset(skip).limit(limit).all()

    return items


@router.post("/", response_model=${1:Resource}Response, status_code=status.HTTP_201_CREATED)
async def create_${2:resource}(
    data: ${1:Resource}Create,
    current_user: User = Depends(get_verified_user),
    db: Session = Depends(get_db)
):
    """
    Create new ${2:resource}

    Requires:
    - User must be verified
    - Valid data according to schema
    """
    logger.info(f"User {current_user.id} creating ${2:resource}")

    try:
        # Create instance
        item = ${1:Resource}(**data.dict(), user_id=current_user.id)

        db.add(item)
        db.commit()
        db.refresh(item)

        logger.info(f"Created ${2:resource} {item.id}")
        return item

    except Exception as e:
        logger.error(f"Error creating ${2:resource}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating ${2:resource}"
        )


@router.get("/{id}", response_model=${1:Resource}Response)
async def get_${2:resource}(
    id: int,
    current_user: User = Depends(get_verified_user),
    db: Session = Depends(get_db)
):
    """Get ${2:resource} by ID"""
    item = db.query(${1:Resource}).filter(${1:Resource}.id == id).first()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="${1:Resource} not found"
        )

    # Check ownership or permissions
    if item.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this ${2:resource}"
        )

    return item


@router.put("/{id}", response_model=${1:Resource}Response)
async def update_${2:resource}(
    id: int,
    data: ${1:Resource}Update,
    current_user: User = Depends(get_verified_user),
    db: Session = Depends(get_db)
):
    """Update ${2:resource}"""
    item = db.query(${1:Resource}).filter(${1:Resource}.id == id).first()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="${1:Resource} not found"
        )

    if item.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this ${2:resource}"
        )

    # Update fields
    for field, value in data.dict(exclude_unset=True).items():
        setattr(item, field, value)

    item.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(item)

    logger.info(f"Updated ${2:resource} {item.id}")
    return item


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_${2:resource}(
    id: int,
    current_user: User = Depends(get_verified_user),
    db: Session = Depends(get_db)
):
    """Delete ${2:resource}"""
    item = db.query(${1:Resource}).filter(${1:Resource}.id == id).first()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="${1:Resource} not found"
        )

    if item.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this ${2:resource}"
        )

    db.delete(item)
    db.commit()

    logger.info(f"Deleted ${2:resource} {id}")
    return None


@router.get("/stats", response_model=dict)
async def get_${2:resource}_stats(
    current_user: User = Depends(get_verified_user),
    db: Session = Depends(get_db)
):
    """Get statistics for ${2:resource}"""
    total = db.query(${1:Resource}).count()
    user_count = db.query(${1:Resource}).filter(
        ${1:Resource}.user_id == current_user.id
    ).count()

    return {
        "total": total,
        "user_count": user_count,
        "created_today": 0,  # Implement based on your needs
        "created_this_week": 0,
        "created_this_month": 0
    }
