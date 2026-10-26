from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from config.db import SessionLocal
from anime.schema import AnimeResponse
from anime import services

router = APIRouter(
    prefix="",
    tags=["Anime"]
)


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("", response_model=List[AnimeResponse])
def read_anime_list(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return services.get_all_anime(db, skip=skip, limit=limit)


@router.get("/{anime_id}", response_model=AnimeResponse)
def read_anime_item(anime_id: int, db: Session = Depends(get_db)):
    anime = services.get_anime_by_id(db, anime_id)
    if not anime:
        raise HTTPException(status_code=404, detail="Anime not found")
    return anime