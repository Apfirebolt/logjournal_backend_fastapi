from sqlalchemy.orm import Session
from anime.models import Anime


def get_all_anime(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Anime).offset(skip).limit(limit).all()


def get_anime_by_id(db: Session, anime_id: int):
    return db.query(Anime).filter(Anime.id == anime_id).first()