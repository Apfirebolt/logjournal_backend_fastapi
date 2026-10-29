from datetime import datetime
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

def _get_user_tags_sync(user_id: int) -> List[models.Tag]:
    db: Session = sync_db.SessionLocal()
    try:
        return db.query(models.Tag).filter(models.Tag.user_id == user_id).order_by(models.Tag.name).all()
    finally:
        db.close()


def _get_or_create_tags_sync(db: Session, user_id: int, tag_names: List[str]) -> List[models.Tag]:
    tag_objects = []
    for name in tag_names:
        cleaned_name = name.strip()
        if not cleaned_name:
            continue
        tag = db.query(models.Tag).filter(
            models.Tag.user_id == user_id,
            models.Tag.name.ilike(cleaned_name)
        ).first()
        
        if not tag:
            tag = models.Tag(name=cleaned_name, user_id=user_id)
            db.add(tag)
            db.flush()
            
        tag_objects.append(tag)
    return tag_objects


def _create_entry_sync(user_id: int, entry_data: schema.JournalEntryCreate) -> models.JournalEntry:
    db: Session = sync_db.SessionLocal()
    try:
        new_entry = models.JournalEntry(
            user_id=user_id,
            title=entry_data.title,
            highlights=entry_data.highlights,
            gratitude=entry_data.gratitude,
            better_day_thoughts=entry_data.better_day_thoughts,
            journal_date=entry_data.journal_date or datetime.utcnow()
        )
        db.add(new_entry)
        db.flush()  # Generates entry.id

        # Process and link tags
        if entry_data.tags:
            new_entry.tags = _get_or_create_tags_sync(db, user_id, entry_data.tags)

        # Add category sections
        for section in entry_data.category_sections:
            section_obj = models.JournalEntryCategory(
                entry_id=new_entry.id,
                category_id=section.category_id,
                content=section.content,
                rating_score=section.rating_score
            )
            db.add(section_obj)

        # Add habits
        for habit in entry_data.habits:
            habit_obj = models.JournalHabit(
                entry_id=new_entry.id,
                task_name=habit.task_name,
                is_completed=habit.is_completed
            )
            db.add(habit_obj)

        db.commit()
        
        # Re-query with relationships loaded
        return db.query(models.JournalEntry).options(
            joinedload(models.JournalEntry.category_sections).joinedload(models.JournalEntryCategory.category),
            joinedload(models.JournalEntry.habits),
            joinedload(models.JournalEntry.tags)
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
            joinedload(models.JournalEntry.category_sections).joinedload(models.JournalEntryCategory.category),
            joinedload(models.JournalEntry.habits),
            joinedload(models.JournalEntry.tags)
        ).filter(models.JournalEntry.id == entry_id, models.JournalEntry.user_id == user_id).first()
    finally:
        db.close()


def _get_entries_sync(user_id: int) -> List[models.JournalEntry]:
    db: Session = sync_db.SessionLocal()
    try:
        return db.query(models.JournalEntry).options(
            joinedload(models.JournalEntry.category_sections).joinedload(models.JournalEntryCategory.category),
            joinedload(models.JournalEntry.habits),
            joinedload(models.JournalEntry.tags)
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


def _get_entry_by_date_sync(user_id: int, date: str) -> Optional[models.JournalEntry]:
    db: Session = sync_db.SessionLocal()
    try:
        return db.query(models.JournalEntry).options(
            joinedload(models.JournalEntry.category_sections).joinedload(models.JournalEntryCategory.category),
            joinedload(models.JournalEntry.habits),
            joinedload(models.JournalEntry.tags)
        ).filter(models.JournalEntry.user_id == user_id, models.JournalEntry.journal_date == date).first()
    finally:
        db.close()


def _update_entry_sync(entry_id: int, user_id: int, entry_data: schema.JournalEntryUpdate) -> models.JournalEntry:
    db: Session = sync_db.SessionLocal()
    try:
        entry = db.query(models.JournalEntry).filter(models.JournalEntry.id == entry_id, models.JournalEntry.user_id == user_id).first()
        if not entry:
            raise Exception("Journal entry not found")

        update_data = entry_data.dict(exclude_unset=True)
        category_sections_data = update_data.pop("category_sections", None)
        habits_data = update_data.pop("habits", None)
        tags_data = update_data.pop("tags", None)

        for key, value in update_data.items():
            setattr(entry, key, value)

        # Update tags if provided
        if tags_data is not None:
            entry.tags = _get_or_create_tags_sync(db, user_id, tags_data)

        # Update category sections if provided
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

        # Update habits if provided
        if habits_data is not None:
            db.query(models.JournalHabit).filter(models.JournalHabit.entry_id == entry.id).delete()
            for habit in habits_data:
                habit_obj = models.JournalHabit(
                    entry_id=entry.id,
                    task_name=habit["task_name"],
                    is_completed=habit.get("is_completed", False)
                )
                db.add(habit_obj)

        db.commit()
        
        return db.query(models.JournalEntry).options(
            joinedload(models.JournalEntry.category_sections).joinedload(models.JournalEntryCategory.category),
            joinedload(models.JournalEntry.habits),
            joinedload(models.JournalEntry.tags)
        ).filter(models.JournalEntry.id == entry.id).first()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# Async wrappers using thread pool
async def get_categories(user_id: int) -> List[models.Category]:
    return await run_in_threadpool(_get_categories_sync, user_id)

async def create_category(user_id: int, name: str) -> models.Category:
    return await run_in_threadpool(_create_category_sync, user_id, name)

async def create_entry(user_id: int, entry_data: schema.JournalEntryCreate) -> models.JournalEntry:
    return await run_in_threadpool(_create_entry_sync, user_id, entry_data)

async def get_entry_by_id(entry_id: int, user_id: int) -> Optional[models.JournalEntry]:
    return await run_in_threadpool(_get_entry_by_id_sync, entry_id, user_id)

async def get_entries(user_id: int) -> List[models.JournalEntry]:
    return await run_in_threadpool(_get_entries_sync, user_id)

async def update_entry(entry_id: int, user_id: int, entry_data: schema.JournalEntryUpdate) -> models.JournalEntry:
    return await run_in_threadpool(_update_entry_sync, entry_id, user_id, entry_data)

async def delete_entry(entry_id: int, user_id: int) -> None:
    return await run_in_threadpool(_delete_entry_sync, entry_id, user_id)

async def get_entry_by_date(user_id: int, date: str) -> Optional[models.JournalEntry]:
    return await run_in_threadpool(_get_entry_by_date_sync, user_id, date)

async def get_user_tags(user_id: int) -> List[models.Tag]:
    return await run_in_threadpool(_get_user_tags_sync, user_id)