from pydantic import BaseModel, field_validator
from typing import List, Optional, Any, Dict
from pydantic import Field
from datetime import datetime

class TagResponse(BaseModel):
    id: int
    name: str
    user_id: int

    class Config:
        from_attributes = True


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


class HabitBase(BaseModel):
    task_name: str
    is_completed: Optional[bool] = False

class HabitCreate(HabitBase):
    pass

class HabitResponse(HabitBase):
    id: int
    entry_id: int

    class Config:
        from_attributes = True


# Input/Output schema for category-specific content and rating inside an entry
class EntryCategorySectionCreate(BaseModel):
    category_id: int
    content: Optional[Any] = None      
    rating_score: Optional[float] = None


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
    highlights: Optional[Any] = None          
    gratitude: Optional[Any] = None           
    better_day_thoughts: Optional[Any] = None
    journal_date: Optional[datetime] = None
    
    category_sections: List[EntryCategorySectionCreate] = []
    habits: List[HabitCreate] = []
    tags: List[str] = Field(default=[], max_length=5, description="Maximum of 5 tags allowed per entry")

    @field_validator('tags')
    def validate_tags(cls, v):
        if len(v) > 5:
            raise ValueError('A journal entry can have a maximum of 5 tags.')
        return [tag.strip() for tag in v if tag.strip()]


class JournalEntryUpdate(BaseModel):
    title: Optional[str] = None
    highlights: Optional[Any] = None
    gratitude: Optional[Any] = None
    better_day_thoughts: Optional[Any] = None
    journal_date: Optional[datetime] = None

    category_sections: Optional[List[EntryCategorySectionCreate]] = None
    habits: Optional[List[HabitCreate]] = None
    tags: Optional[List[str]] = Field(default=None, max_length=5)

    @field_validator('tags')
    def validate_tags(cls, v):
        if v is not None:
            if len(v) > 5:
                raise ValueError('A journal entry can have a maximum of 5 tags.')
            return [tag.strip() for tag in v if tag.strip()]
        return v


class JournalEntryResponse(BaseModel):
    id: int
    user_id: int
    title: Optional[str] = None
    highlights: Optional[Any] = None
    gratitude: Optional[Any] = None
    journal_date: Optional[datetime] = None
    better_day_thoughts: Optional[Any] = None
    created_at: datetime
    updated_at: datetime
    
    category_sections: List[EntryCategorySectionResponse] = []
    habits: List[HabitResponse] = []
    tags: List[str] = []

    @field_validator('tags', mode='before')
    def extract_tag_names(cls, v):
        if v and isinstance(v, list):
            return [tag.name if hasattr(tag, 'name') else tag for tag in v]
        return v

    class Config:
        from_attributes = True