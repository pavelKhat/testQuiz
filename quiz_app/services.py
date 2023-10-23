"""Module with service functions for quiz app."""
import requests

from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound

from .models import Question
from .schemas import QuestionsModel

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
                    session: Session) -> None:
    """Function that safe questions to database."""
    session.add_all(
        [Question(item.model_dump()) for item in questions_list]
    )
    session.commit()


def _get_stored_ids(session: Session) -> set:
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


def get_previous_stored_question(session: Session) -> QuestionsModel | HTTPException:
    """Functions that returns last stored question."""

    try:
        question = session.query(Question).order_by(Question.stored_at.desc()).limit(1).one()
    except NoResultFound:
        return HTTPException(400, detail="Where is no saved questions yet.")
    return QuestionsModel.model_validate(question)


def collect_questions(session: Session, count: int) -> None:
    """Functions that collect and safe questions."""
    try:
        data = _get_questions_from_api(count)
        questions = _transform_data(data)
        questions = _avoid_duplicates(session, questions, count)
        _safe_questions(questions, session)
    except Exception as error:
        raise HTTPException(400, detail=f"{error.args}")
