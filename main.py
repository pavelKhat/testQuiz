"""Module with main app."""
from fastapi import FastAPI

from database import init_db
from quiz_app import quiz_router


init_db()

app = FastAPI(title="Quiz questions App!")

app.include_router(quiz_router)
