"""Module with main app."""
from typing import Union

import requests
from datetime import datetime

from fastapi import Depends
from fastapi import FastAPI
from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy import desc
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session


# DB
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/postgres"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db: Session = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()


# Schemas & Model
class QuestionsPostRequest(BaseModel):
    questions_num: int


class QuestionsModel(BaseModel):
    id: int
    question: str
    answer: str
    created_at: datetime

    class Config:
        from_attributes = True


class QuestionPostResponse(BaseModel):
    data: list[QuestionsModel] = None


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


Base.metadata.create_all(bind=engine)


# Services for questions
API_URL_TEMPLATE = "https://jservice.io/api/random?count={}"


def _get_questions_from_api(question_count: int) -> list[dict]:
    """Function that loads questions form external API."""
    url = API_URL_TEMPLATE.format(question_count)
    try:
        response = requests.get(url).json()
    except requests.HTTPError as error:
        raise HTTPException(400, detail=f"{error.request} was unsuccesseful! {error}")
    return response


def _transform_data(json_data: list[dict]) -> list[QuestionsModel]:
    results = []
    for item in json_data:
        new_q = QuestionsModel.model_validate(item)
        results.append(new_q)
    return results


def _safe_questions(questions_list: list[QuestionsModel],
                    session: SessionLocal) -> None:
    """Function that safe questions to database."""
    session.add_all(
        [Question(item.model_dump()) for item in questions_list]
    )
    session.commit()


def _get_stored_ids(session: SessionLocal) -> set:
    """Function that load ids of stored questions."""
    stored_ids = set([
        i[0] for i in session.query(Question).with_entities(Question.id).all()
    ])
    return stored_ids


def _avoid_duplicates(
        session: Session,
        questions_list: list[QuestionsModel],
        count: int) -> list[QuestionsModel]:
    """Function that search and replace duplicates."""
    questions_list = questions_list[:]
    stored_ids = _get_stored_ids(session)
    result = []
    while len(result) < count:
        for question in questions_list:
            if question.id not in stored_ids:
                result.append(question)
                questions_list.remove(question)
                continue
            else:
                questions_list.remove(question)
                new_question = _get_questions_from_api(1)
                result.extend(_transform_data(new_question))
    return result


def _get_previous_stored_question(session: Session) -> QuestionsModel | HTTPException:
    """Functions that returns last stored question."""

    try:
        question = session.query(Question).order_by(desc(Question.stored_at)).limit(1).one()
    except NoResultFound:
        return HTTPException(400, detail="Where is no saved questions yet.")
    return QuestionsModel.model_validate(question)


# FastAPI
app = FastAPI(title="Quiz questions App!")


@app.post('/questions', response_model=None)
def post_questions(request: QuestionsPostRequest,
                   session: Session = Depends(get_db)) -> Union[QuestionsModel, HTTPException]:
    """Endpoint for Questions post request."""

    response = _get_previous_stored_question(session)
    data = _get_questions_from_api(request.questions_num)
    questions = _transform_data(data)
    questions = _avoid_duplicates(session, questions, request.questions_num)
    _safe_questions(questions, session)

    return response
