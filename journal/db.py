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

def _get_entry_by_id_sync(entry_id: int, user_id: int) -> Optional[models.JournalEntry]:
    db: Session = sync_db.SessionLocal()
    try:
        return db.query(models.JournalEntry).options(
            joinedload(models.JournalEntry.category_sections).joinedload(models.JournalEntryCategory.category)
        ).filter(models.JournalEntry.id == entry_id, models.JournalEntry.user_id == user_id).first()
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


def _delete_entry_sync(entry_id: int, user_id: int) -> None:
    db: Session = sync_db.SessionLocal()
    try:
        entry = db.query(models.JournalEntry).filter(models.JournalEntry.id == entry_id, models.JournalEntry.user_id == user_id).first()
        if entry:
            db.delete(entry)
            db.commit()
    finally:
        db.close()


def _update_entry_sync(entry_id: int, user_id: int, entry_data: schema.JournalEntryUpdate) -> models.JournalEntry:
    db: Session = sync_db.SessionLocal()
    try:
        entry = db.query(models.JournalEntry).filter(models.JournalEntry.id == entry_id, models.JournalEntry.user_id == user_id).first()
        if not entry:
            raise Exception("Journal entry not found")

        # Update scalar fields
        update_data = entry_data.dict(exclude_unset=True)
        category_sections_data = update_data.pop("category_sections", None)

        for key, value in update_data.items():
            setattr(entry, key, value)

        # If category sections are provided in the update, replace them
        if category_sections_data is not None:
            db.query(models.JournalEntryCategory).filter(models.JournalEntryCategory.entry_id == entry.id).delete()
            for section in category_sections_data:
                section_obj = models.JournalEntryCategory(
                    entry_id=entry.id,
                    category_id=section["category_id"],
                    content=section.get("content"),
                    rating_score=section.get("rating_score")
                )
                db.add(section_obj)

        db.commit()
        
        # Return with relationships loaded
        return db.query(models.JournalEntry).options(
            joinedload(models.JournalEntry.category_sections).joinedload(models.JournalEntryCategory.category)
        ).filter(models.JournalEntry.id == entry.id).first()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# Async wrappers using thread pool
async def get_categories(user_id: int) -> List[models.Category]:
    return await run_in_threadpool(_get_categories_sync, user_id)

async def get_entry_by_id(entry_id: int, user_id: int) -> Optional[models.JournalEntry]:
    return await run_in_threadpool(_get_entry_by_id_sync, entry_id, user_id)

async def get_entries(user_id: int) -> List[models.JournalEntry]:
    return await run_in_threadpool(_get_entries_sync, user_id)

async def delete_entry(entry_id: int, user_id: int) -> None:
    return await run_in_threadpool(_delete_entry_sync, entry_id, user_id)

async def update_entry(entry_id: int, user_id: int, entry_data: schema.JournalEntryUpdate) -> models.JournalEntry:
    return await run_in_threadpool(_update_entry_sync, entry_id, user_id, entry_data)

async def create_category(user_id: int, name: str) -> models.Category:
    return await run_in_threadpool(_create_category_sync, user_id, name)

async def create_entry(user_id: int, entry_data: schema.JournalEntryCreate) -> models.JournalEntry:
    return await run_in_threadpool(_create_entry_sync, user_id, entry_data)

async def update_entry(entry_id: int, user_id: int, entry_data: schema.JournalEntryUpdate) -> models.JournalEntry:
    return await run_in_threadpool(_update_entry_sync, entry_id, user_id, entry_data)

async def get_entries(user_id: int) -> List[models.JournalEntry]:
    return await run_in_threadpool(_get_entries_sync, user_id)

async def delete_entry(entry_id: int, user_id: int) -> None:
    return await run_in_threadpool(_delete_entry_sync, entry_id, user_id)
