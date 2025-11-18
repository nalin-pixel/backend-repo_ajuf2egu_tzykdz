"""
Database Schemas for Trip Itinerary Aggregator

Each Pydantic model represents a collection in MongoDB.
Collection name is the lowercase of the class name.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime

class Itinerary(BaseModel):
    """
    Collection: "itinerary"
    Represents a user's trip container with a date range and optional locations.
    """
    name: str = Field(..., description="Itinerary name")
    start_date: datetime = Field(..., description="Start date of itinerary")
    end_date: datetime = Field(..., description="End date of itinerary")
    locations: List[str] = Field(default_factory=list, description="Primary cities/locations")
    notes: Optional[str] = Field(None, description="General notes")

class Reservation(BaseModel):
    """
    Collection: "reservation"
    A single reservation item associated with an itinerary.
    """
    itinerary_id: str = Field(..., description="Related itinerary id (ObjectId as string)")
    provider: str = Field(..., description="Source provider, e.g., booking.com, agoda, viator")
    category: Literal["lodging", "flight", "activity", "transport", "dining", "other"] = Field(
        "other", description="Type of reservation"
    )
    title: str = Field(..., description="Display title, e.g., Hotel name or Activity name")
    location: Optional[str] = Field(None, description="City or address")
    start_time: Optional[datetime] = Field(None, description="Start/check-in/dep time")
    end_time: Optional[datetime] = Field(None, description="End/check-out/arr time")
    confirmation_number: Optional[str] = Field(None, description="Booking reference")
    details: Optional[dict] = Field(default_factory=dict, description="Misc structured details")
    source: Optional[str] = Field(None, description="email|api|manual|import")

class Account(BaseModel):
    """
    Collection: "account"
    Connected account metadata (placeholder for OAuth connections).
    """
    provider: Literal[
        "email", "booking.com", "agoda", "viator", "klook", "getyourguide"
    ]
    label: Optional[str] = Field(None, description="Display label for the connection")
    status: Literal["connected", "pending", "error"] = Field("pending")
    credentials_ref: Optional[str] = Field(None, description="Reference to stored credentials (external vault)")
    last_sync_at: Optional[datetime] = Field(None, description="Last time we synced from this account")
