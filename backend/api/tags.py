from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
import uuid

from ..db import get_db
from ..models import Tag, CampaignTag, AssetTag, Campaign, Asset
from ..schemas import (
    TagCreate, TagUpdate, TagRead, 
    CampaignTagCreate, AssetTagCreate,
    TaggedItem, TagStats
)

router = APIRouter(prefix="/tags", tags=["tags"])

@router.post("/", response_model=TagRead)
def create_tag(payload: TagCreate, db: Session = Depends(get_db)):
    """Create a new tag."""
    # Check for existing tag with same name
    existing = db.query(Tag).filter_by(name=payload.name).first()
    if existing:
        raise HTTPException(400, detail="Tag already exists")
    
    # Create new tag
    tag = Tag(
        tag_id=str(uuid.uuid4()),
        name=payload.name,
        description=payload.description
    )
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag

@router.get("/", response_model=List[TagRead])
def list_tags(
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all tags, optionally filtered by search term."""
    query = db.query(Tag)
    if search:
        query = query.filter(Tag.name.ilike(f"%{search}%"))
    return query.order_by(Tag.name).all()

@router.get("/{tag_id}", response_model=TagRead)
def get_tag(tag_id: str, db: Session = Depends(get_db)):
    """Get a specific tag by ID."""
    tag = db.query(Tag).get(tag_id)
    if not tag:
        raise HTTPException(404, detail="Tag not found")
    return tag

@router.patch("/{tag_id}", response_model=TagRead)
def update_tag(tag_id: str, payload: TagUpdate, db: Session = Depends(get_db)):
    """Update a tag's name or description."""
    tag = db.query(Tag).get(tag_id)
    if not tag:
        raise HTTPException(404, detail="Tag not found")
    
    # Check if new name conflicts with existing tag
    if payload.name != tag.name:
        existing = db.query(Tag).filter_by(name=payload.name).first()
        if existing:
            raise HTTPException(400, detail="Tag name already exists")
    
    tag.name = payload.name
    tag.description = payload.description
    db.commit()
    return tag

@router.delete("/{tag_id}", status_code=204)
def delete_tag(tag_id: str, db: Session = Depends(get_db)):
    """Delete a tag and its associations."""
    tag = db.query(Tag).get(tag_id)
    if not tag:
        raise HTTPException(404, detail="Tag not found")
    
    # Delete associations first
    db.query(CampaignTag).filter_by(tag_id=tag_id).delete()
    db.query(AssetTag).filter_by(tag_id=tag_id).delete()
    
    # Delete the tag
    db.delete(tag)
    db.commit()

@router.post("/campaigns/{campaign_id}", response_model=List[TagRead])
def tag_campaign(
    campaign_id: str,
    payload: CampaignTagCreate,
    db: Session = Depends(get_db)
):
    """Add tags to a campaign."""
    # Verify campaign exists
    campaign = db.query(Campaign).get(campaign_id)
    if not campaign:
        raise HTTPException(404, detail="Campaign not found")
    
    # Verify all tags exist
    tags = db.query(Tag).filter(Tag.tag_id.in_(payload.tag_ids)).all()
    if len(tags) != len(payload.tag_ids):
        raise HTTPException(400, detail="One or more tags not found")
    
    # Add associations
    for tag in tags:
        assoc = CampaignTag(
            campaign_id=campaign_id,
            tag_id=tag.tag_id
        )
        db.add(assoc)
    
    db.commit()
    return tags

@router.post("/assets/{asset_id}", response_model=List[TagRead])
def tag_asset(
    asset_id: str,
    payload: AssetTagCreate,
    db: Session = Depends(get_db)
):
    """Add tags to an asset."""
    # Verify asset exists
    asset = db.query(Asset).get(asset_id)
    if not asset:
        raise HTTPException(404, detail="Asset not found")
    
    # Verify all tags exist
    tags = db.query(Tag).filter(Tag.tag_id.in_(payload.tag_ids)).all()
    if len(tags) != len(payload.tag_ids):
        raise HTTPException(400, detail="One or more tags not found")
    
    # Add associations
    for tag in tags:
        assoc = AssetTag(
            asset_id=asset_id,
            tag_id=tag.tag_id
        )
        db.add(assoc)
    
    db.commit()
    return tags

@router.get("/stats", response_model=List[TagStats])
def get_tag_stats(db: Session = Depends(get_db)):
    """Get usage statistics for all tags."""
    return db.query(
        Tag.tag_id,
        Tag.name,
        func.count(CampaignTag.campaign_id).label('campaign_count'),
        func.count(AssetTag.asset_id).label('asset_count')
    ).outerjoin(CampaignTag).outerjoin(AssetTag).group_by(Tag.tag_id, Tag.name).all() 