from typing import Optional
from pydantic import BaseModel


class AnimeBase(BaseModel):
    mal_id: Optional[int] = None
    title: str
    title_english: Optional[str] = None
    title_japanese: Optional[str] = None
    type: Optional[str] = None
    source: Optional[str] = None
    episodes: Optional[int] = None
    status: Optional[str] = None
    airing: Optional[bool] = None
    aired_from: Optional[str] = None
    aired_to: Optional[str] = None
    duration: Optional[str] = None
    rating: Optional[str] = None
    score: Optional[float] = None
    scored_by: Optional[int] = None
    rank: Optional[int] = None
    popularity: Optional[int] = None
    members: Optional[int] = None
    favorites: Optional[int] = None
    season: Optional[str] = None
    year: Optional[int] = None
    studios: Optional[str] = None
    producers: Optional[str] = None
    licensors: Optional[str] = None
    genres: Optional[str] = None
    themes: Optional[str] = None
    demographics: Optional[str] = None
    synopsis: Optional[str] = None
    image_url: Optional[str] = None


class AnimeCreate(AnimeBase):
    pass


class AnimeResponse(AnimeBase):
    id: int

    model_config = {
        "from_attributes": True
    }