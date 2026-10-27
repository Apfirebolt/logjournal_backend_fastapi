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


class JournalEntryUpdate(BaseModel):
    title: Optional[str] = None
    highlights: Optional[Any] = None
    gratitude: Optional[Any] = None
    better_day_thoughts: Optional[Any] = None
    journal_date: Optional[datetime] = None
    
    category_sections: Optional[List[EntryCategorySectionCreate]] = None
    habits: Optional[List[HabitCreate]] = None


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
    habits: List[HabitResponse] = []

    class Config:
        from_attributes = True