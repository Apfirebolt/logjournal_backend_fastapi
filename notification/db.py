from typing import List, Optional
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session
from config import db as sync_db
from . import models, schema

def _get_notifications_sync(user_id: int) -> List[models.Notification]:
    db: Session = sync_db.SessionLocal()
    try:
        return db.query(models.Notification).filter(
            models.Notification.user_id == user_id
        ).order_by(models.Notification.created_at.desc()).all()
    finally:
        db.close()

def _create_notification_sync(user_id: int, data: schema.NotificationCreate) -> models.Notification:
    db: Session = sync_db.SessionLocal()
    try:
        notification = models.Notification(
            user_id=user_id,
            title=data.title,
            message=data.message,
            notification_type=data.notification_type,
            is_read=False
        )
        db.add(notification)
        db.commit()
        db.refresh(notification)
        return notification
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def _mark_as_read_sync(notification_id: int, user_id: int) -> Optional[models.Notification]:
    db: Session = sync_db.SessionLocal()
    try:
        notification = db.query(models.Notification).filter(
            models.Notification.id == notification_id,
            models.Notification.user_id == user_id
        ).first()
        
        if notification:
            notification.is_read = True
            db.commit()
            db.refresh(notification)
        return notification
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def _delete_notification_sync(notification_id: int, user_id: int) -> None:
    db: Session = sync_db.SessionLocal()
    try:
        notification = db.query(models.Notification).filter(
            models.Notification.id == notification_id,
            models.Notification.user_id == user_id
        ).first()
        if notification:
            db.delete(notification)
            db.commit()
    finally:
        db.close()

# Async Wrappers
async def get_user_notifications(user_id: int) -> List[models.Notification]:
    return await run_in_threadpool(_get_notifications_sync, user_id)

async def create_notification(user_id: int, data: schema.NotificationCreate) -> models.Notification:
    return await run_in_threadpool(_create_notification_sync, user_id, data)

async def mark_notification_read(notification_id: int, user_id: int) -> Optional[models.Notification]:
    return await run_in_threadpool(_mark_as_read_sync, notification_id, user_id)

async def delete_notification(notification_id: int, user_id: int) -> None:
    return await run_in_threadpool(_delete_notification_sync, notification_id, user_id)