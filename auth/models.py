from sqlalchemy import Column, Integer, String
from typing import Any
from config.db import Base

from .import hashing


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50))
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    email = Column(String(255), unique=True)
    role = Column(String(50), nullable=True, default='user')
    password = Column(String(255))

    def __init__(self, username: str, email: str, role: str, password: str, first_name: str = None, last_name: str = None, *args: Any, **kwargs: Any) -> None:
        self.username = username
        self.email = email
        self.role = role
        self.password = hashing.get_password_hash(password)
        self.first_name = first_name
        self.last_name = last_name

    def check_password(self, password: str) -> bool:
        return hashing.verify_password(password, self.password)
