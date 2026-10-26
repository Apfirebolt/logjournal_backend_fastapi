from typing import List, Optional

from dotenv import load_dotenv
load_dotenv()

from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session

from config import db as sync_db
from . import models


def _create_user_sync(username: str, email: str, password: str, role: str = 'user') -> models.User:
    db: Session = sync_db.SessionLocal()
    try:
        new_user = models.User(username=username, email=email, role=role, password=password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def _get_user_by_email_sync(email: str) -> Optional[models.User]:
    db: Session = sync_db.SessionLocal()
    try:
        return db.query(models.User).filter(models.User.email == email).first()
    finally:
        db.close()


def _get_user_by_id_sync(user_id: int) -> Optional[models.User]:
    db: Session = sync_db.SessionLocal()
    try:
        return db.query(models.User).get(user_id)
    finally:
        db.close()


def _get_all_users_sync() -> List[models.User]:
    db: Session = sync_db.SessionLocal()
    try:
        return db.query(models.User).all()
    finally:
        db.close()


async def create_user(username: str, email: str, password: str, role: str = 'user') -> models.User:
    return await run_in_threadpool(_create_user_sync, username, email, password, role)


async def get_user_by_email(email: str) -> Optional[models.User]:
    return await run_in_threadpool(_get_user_by_email_sync, email)


async def get_user_by_id(user_id: int) -> Optional[models.User]:
    return await run_in_threadpool(_get_user_by_id_sync, user_id)


async def get_all_users() -> List[models.User]:
    return await run_in_threadpool(_get_all_users_sync)


def _update_user_password_sync(user_id: int, new_hashed_password: str) -> Optional[models.User]:
    db: Session = sync_db.SessionLocal()
    try:
        user = db.query(models.User).get(user_id)
        if not user:
            return None
        user.password = new_hashed_password
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


async def update_user_password(user_id: int, new_hashed_password: str) -> Optional[models.User]:
    return await run_in_threadpool(_update_user_password_sync, user_id, new_hashed_password)
