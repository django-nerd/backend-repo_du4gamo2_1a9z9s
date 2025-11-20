"""
Database Schemas for AURCA SOUND

Each Pydantic model corresponds to a MongoDB collection (lowercased class name).
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class Artist(BaseModel):
    stage_name: str = Field(..., description="Public artist name")
    user_id: Optional[str] = Field(None, description="Linked auth user id")
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    socials: Optional[dict] = Field(default_factory=dict)
    dsps: Optional[dict] = Field(default_factory=dict)

class Track(BaseModel):
    title: str = Field(..., description="Track title")
    primary_artist: str = Field(..., description="Primary artist display name")
    featuring: List[str] = Field(default_factory=list, description="Featuring artists")
    isrc: Optional[str] = Field(None, description="ISRC code")
    upc: Optional[str] = Field(None, description="UPC/EAN for single if applicable")
    explicit: bool = Field(False, description="Explicit content flag")
    genre: Optional[str] = None
    mood: Optional[str] = None
    cover_url: Optional[str] = None
    audio_url: Optional[str] = None
    release_date: Optional[datetime] = None
    status: str = Field("draft", description="draft | scheduled | released | archived")
    ai_mastering: bool = Field(False, description="Enable AI mastering pipeline")
    metadata: dict = Field(default_factory=dict)

class Release(BaseModel):
    title: str = Field(..., description="Release title")
    type: str = Field("single", description="single | ep | album")
    upc: Optional[str] = None
    cover_url: Optional[str] = None
    release_date: Optional[datetime] = None
    tracks: List[str] = Field(default_factory=list, description="Array of track document IDs")
    status: str = Field("draft")
    notes: Optional[str] = None

# Additional modules will define their own models as we expand (events, escrow, merch, etc.)
