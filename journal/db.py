from typing import List, Optional
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session, joinedload
from config import db as sync_db
from . import models, schema


def _get_categories_sync(user_id: int) -> List[models.Category]:
    db: Session = sync_db.SessionLocal()
    try:
        return db.query(models.Category).filter(
            (models.Category.is_default == 1) | (models.Category.user_id == user_id)
        ).all()
    finally:
        db.close()


def _create_category_sync(user_id: int, name: str) -> models.Category:
    db: Session = sync_db.SessionLocal()
    try:
        category = models.Category(name=name, is_default=0, user_id=user_id)
        db.add(category)
        db.commit()
        db.refresh(category)
        return category
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def _create_entry_sync(user_id: int, entry_data: schema.JournalEntryCreate) -> models.JournalEntry:
    db: Session = sync_db.SessionLocal()
    try:
        new_entry = models.JournalEntry(
            user_id=user_id,
            title=entry_data.title,
            highlights=entry_data.highlights,
            gratitude=entry_data.gratitude,
            better_day_thoughts=entry_data.better_day_thoughts
        )
        db.add(new_entry)
        db.flush()  # Generates entry.id

        for section in entry_data.category_sections:
            section_obj = models.JournalEntryCategory(
                entry_id=new_entry.id,
                category_id=section.category_id,
                content=section.content,
                rating_score=section.rating_score
            )
            db.add(section_obj)

        db.commit()
        
        # Re-query with joined relationships loaded for response validation
        return db.query(models.JournalEntry).options(
            joinedload(models.JournalEntry.category_sections).joinedload(models.JournalEntryCategory.category)
        ).filter(models.JournalEntry.id == new_entry.id).first()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def _get_entries_sync(user_id: int) -> List[models.JournalEntry]:
    db: Session = sync_db.SessionLocal()
    try:
        return db.query(models.JournalEntry).options(
            joinedload(models.JournalEntry.category_sections).joinedload(models.JournalEntryCategory.category)
        ).filter(models.JournalEntry.user_id == user_id).all()
    finally:
        db.close()


def _get_entry_by_id_sync(entry_id: int, user_id: int) -> Optional[models.JournalEntry]:
    db: Session = sync_db.SessionLocal()
    try:
        return db.query(models.JournalEntry).options(
            joinedload(models.JournalEntry.category_sections).joinedload(models.JournalEntryCategory.category)
        ).filter(models.JournalEntry.id == entry_id, models.JournalEntry.user_id == user_id).first()
    finally:
        db.close()


# Async wrappers using thread pool
async def get_categories(user_id: int) -> List[models.Category]:
    return await run_in_threadpool(_get_categories_sync, user_id)

async def create_category(user_id: int, name: str) -> models.Category:
    return await run_in_threadpool(_create_category_sync, user_id, name)

async def create_entry(user_id: int, entry_data: schema.JournalEntryCreate) -> models.JournalEntry:
    return await run_in_threadpool(_create_entry_sync, user_id, entry_data)

async def get_entries(user_id: int) -> List[models.JournalEntry]:
    return await run_in_threadpool(_get_entries_sync, user_id)

async def get_entry_by_id(entry_id: int, user_id: int) -> Optional[models.JournalEntry]:
    return await run_in_threadpool(_get_entry_by_id_sync, entry_id, user_id)