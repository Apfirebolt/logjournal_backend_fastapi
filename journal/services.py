from fastapi import HTTPException, status
from typing import List
from . import schema, models
import journal.db as journal_db


async def fetch_user_categories(user_id: int) -> List[schema.CategoryResponse]:
    categories = await journal_db.get_categories(user_id)
    return [schema.CategoryResponse.model_validate(c) for c in categories]


async def add_custom_category(user_id: int, request: schema.CategoryCreate) -> schema.CategoryResponse:
    category = await journal_db.create_category(user_id, request.name)
    return schema.CategoryResponse.model_validate(category)


async def create_journal_entry(user_id: int, request: schema.JournalEntryCreate) -> schema.JournalEntryResponse:
    try:
        entry = await journal_db.create_entry(user_id, request)
        return schema.JournalEntryResponse.model_validate(entry)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating journal entry: {str(e)}"
        )


async def fetch_user_entries(user_id: int) -> List[schema.JournalEntryResponse]:
    entries = await journal_db.get_entries(user_id)
    return [schema.JournalEntryResponse.model_validate(e) for e in entries]


async def fetch_entry_detail(entry_id: int, user_id: int) -> schema.JournalEntryResponse:
    entry = await journal_db.get_entry_by_id(entry_id, user_id)
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Journal entry not found"
        )
    return schema.JournalEntryResponse.model_validate(entry)