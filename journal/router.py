from fastapi import APIRouter, status, Depends
from typing import List
from . import schema, services
from auth.jwt import get_current_user
from auth import schema as auth_schema

router = APIRouter(tags=['Journal'], prefix='/api/journal')


@router.get('/categories', response_model=List[schema.CategoryResponse])
async def get_categories(current_user: auth_schema.TokenData = Depends(get_current_user)):
    """Fetch default system categories + user custom categories"""
    return await services.fetch_user_categories(current_user.id)


@router.post('/categories', response_model=schema.CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(request: schema.CategoryCreate, current_user: auth_schema.TokenData = Depends(get_current_user)):
    """Allow user to add custom categories (e.g. Friends)"""
    return await services.add_custom_category(current_user.id, request)

@router.get('/tags', response_model=List[schema.TagResponse])
async def get_user_tags(current_user: auth_schema.TokenData = Depends(get_current_user)):
    """Fetch all unique custom tags created by the user"""
    return await services.fetch_user_tags(current_user.id)


@router.post('/entries', response_model=schema.JournalEntryResponse, status_code=status.HTTP_201_CREATED)
async def create_entry(request: schema.JournalEntryCreate, current_user: auth_schema.TokenData = Depends(get_current_user)):
    """Create a daily journal entry with global prompts and optional category HTML sections + ratings"""
    return await services.create_journal_entry(current_user.id, request)


@router.get('/entries', response_model=List[schema.JournalEntryResponse])
async def list_entries(current_user: auth_schema.TokenData = Depends(get_current_user)):
    """Get all journal entries for the logged-in user"""
    return await services.fetch_user_entries(current_user.id)


@router.get('/entries/{entry_id}', response_model=schema.JournalEntryResponse)
async def get_entry_detail(entry_id: int, current_user: auth_schema.TokenData = Depends(get_current_user)):
    """Get a specific journal entry by ID"""
    return await services.fetch_entry_detail(entry_id, current_user.id)

@router.delete('/entries/{entry_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_entry(entry_id: int, current_user: auth_schema.TokenData = Depends(get_current_user)):
    """Delete a specific journal entry by ID"""
    await services.delete_journal_entry(entry_id, current_user.id)
    return {"detail": "Journal entry deleted successfully"}


@router.put('/entries/{entry_id}', response_model=schema.JournalEntryResponse)
async def update_entry(entry_id: int, request: schema.JournalEntryUpdate, current_user: auth_schema.TokenData = Depends(get_current_user)):
    """Update a specific journal entry by ID"""
    return await services.update_journal_entry(entry_id, current_user.id, request)