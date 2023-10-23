"""Module with routes for quiz app."""
from typing import Union

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException


from sqlalchemy.orm import Session

from database import get_db

from . import services as srv
from .schemas import QuestionsPostRequest, QuestionsModel


router = APIRouter(tags=["Quiz App"],)


@router.post('/questions', response_model=None)
def post_questions(request: QuestionsPostRequest,
                   session: Session = Depends(get_db)) -> Union[QuestionsModel, HTTPException]:
    """Endpoint for Questions post request."""

    response = srv.get_previous_stored_question(session)
    srv.collect_questions(session, request.questions_num)

    return response
