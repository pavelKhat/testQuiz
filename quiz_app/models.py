"""Module with database models for quiz app."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime

from database import Base


class Question(Base):
    """Class for Question db model."""
    __tablename__ = 'questions'
    id = Column(Integer, primary_key=True)
    question = Column(String)
    answer = Column(String)
    created_at = Column(DateTime)
    stored_at = Column(DateTime, default=lambda x: datetime.utcnow())

    def __init__(self, data: dict):
        for k, v in data.items():
            setattr(self, k, v)
