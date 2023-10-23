"""Module with schemas for quiz app."""
from datetime import datetime

from pydantic import BaseModel


class QuestionsPostRequest(BaseModel):
    questions_num: int


class QuestionsModel(BaseModel):
    id: int
    question: str
    answer: str
    created_at: datetime

    class Config:
        from_attributes = True
