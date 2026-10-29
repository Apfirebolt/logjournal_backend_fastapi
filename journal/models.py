from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, DateTime, Float, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import JSON
from sqlalchemy import UniqueConstraint, Table
from typing import Optional
from sqlalchemy.orm import relationship
from config.db import Base

entry_tags_association = Table(
    "entry_tags_association",
    Base.metadata,
    Column("entry_id", Integer, ForeignKey("journal_entries.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)
)


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    is_default = Column(Integer, default=0)  # 1 for system defaults (Work, Health, Family), 0 for custom
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=True)  # Null for global defaults

    # Relationships
    entry_associations = relationship("JournalEntryCategory", back_populates="category", cascade="all, delete-orphan")


class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=True)
    journal_date = Column(DateTime(timezone=True), nullable=True)
    
    # Global daily reflection prompts (stored as JSONB for rich HTML / block editors)
    highlights = Column(JSONB, nullable=True, default=dict)
    gratitude = Column(JSONB, nullable=True, default=dict)
    better_day_thoughts = Column(JSONB, nullable=True, default=dict)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relationships
    category_sections = relationship("JournalEntryCategory", back_populates="entry", cascade="all, delete-orphan")
    habits = relationship("JournalHabit", back_populates="entry", cascade="all, delete-orphan")
    tags = relationship("Tag", secondary=entry_tags_association, back_populates="entries")


class JournalEntryCategory(Base):
    __tablename__ = "journal_entry_categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    entry_id = Column(Integer, ForeignKey("journal_entries.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)
    
    content = Column(JSONB, nullable=True, default=dict)
    rating_score = Column(Float, nullable=True)

    entry = relationship("JournalEntry", back_populates="category_sections")
    category = relationship("Category", back_populates="entry_associations")

    @property
    def category_name(self) -> Optional[str]:
        return self.category.name if self.category else None


class JournalHabit(Base):
    __tablename__ = "journal_habits"

    id = Column(Integer, primary_key=True, index=True)
    entry_id = Column(Integer, ForeignKey("journal_entries.id", ondelete="CASCADE"), nullable=False)
    task_name = Column(String(255), nullable=False)
    is_completed = Column(Boolean, default=False)

    # Relationship back to entry
    entry = relationship("JournalEntry", back_populates="habits")


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_user_tag_name"),
    )

    # Relationship back to entries
    entries = relationship("JournalEntry", secondary=entry_tags_association, back_populates="tags")