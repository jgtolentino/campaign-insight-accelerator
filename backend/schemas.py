from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid

class TagBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None

class TagCreate(TagBase):
    pass

class TagUpdate(TagBase):
    pass

class TagRead(TagBase):
    tag_id: str
    created_at: datetime
    tenant_id: str

    class Config:
        orm_mode = True

class CampaignTagCreate(BaseModel):
    campaign_id: str
    tag_ids: List[str]

class AssetTagCreate(BaseModel):
    asset_id: str
    tag_ids: List[str]

class TaggedItem(BaseModel):
    id: str
    name: str
    tags: List[TagRead]

class TagStats(BaseModel):
    tag_id: str
    name: str
    campaign_count: int
    asset_count: int 