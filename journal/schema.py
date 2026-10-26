from pydantic import BaseModel
from typing import List, Optional, Any, Dict
from datetime import datetime


class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: int
    is_default: int
    user_id: Optional[int] = None

    class Config:
        from_attributes = True


# Input/Output schema for category-specific content and rating inside an entry
class EntryCategorySectionCreate(BaseModel):
    category_id: int
    content: Optional[Any] = None      # Rich HTML/JSON blocks for this category (nullable)
    rating_score: Optional[float] = None # Rating for this category (nullable)


class EntryCategorySectionResponse(BaseModel):
    id: int
    category_id: int
    category_name: Optional[str] = None
    content: Optional[Any] = None
    rating_score: Optional[float] = None

    class Config:
        from_attributes = True


# Main Journal Entry Schemas
class JournalEntryCreate(BaseModel):
    title: Optional[str] = None
    highlights: Optional[Any] = None          # Global prompt
    gratitude: Optional[Any] = None           # Global prompt
    better_day_thoughts: Optional[Any] = None # Global prompt
    
    # List of category sections (Work, Health, Family, Friends, etc.) Alice chose to fill out today
    category_sections: List[EntryCategorySectionCreate] = []


class JournalEntryUpdate(BaseModel):
    title: Optional[str] = None
    highlights: Optional[Any] = None
    gratitude: Optional[Any] = None
    better_day_thoughts: Optional[Any] = None
    category_sections: Optional[List[EntryCategorySectionCreate]] = None


class JournalEntryResponse(BaseModel):
    id: int
    user_id: int
    title: Optional[str] = None
    highlights: Optional[Any] = None
    gratitude: Optional[Any] = None
    better_day_thoughts: Optional[Any] = None
    created_at: datetime
    updated_at: datetime
    
    # Rendered category sections with their content and ratings
    category_sections: List[EntryCategorySectionResponse] = []

    class Config:
        from_attributes = True