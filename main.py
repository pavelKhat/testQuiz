"""Module with main app."""
import requests
from datetime import datetime

from fastapi import FastAPI
from fastapi import HTTPException
from pydantic import BaseModel


app = FastAPI(title="Quiz questions App!")


# Schemas & Model
class QuestionsPostRequest(BaseModel):
    questions_num: int


class QuestionsModel(BaseModel):
    id: int
    question: str
    answer: str
    created_at: datetime


class QuestionPostResponse(BaseModel):
    data: list[QuestionsModel] = None


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


@app.post('/questions', response_model=QuestionPostResponse)
def post_questions(request: QuestionsPostRequest):
    """Endpoint for Questions post request, """
    data = _get_questions_from_api(request.questions_num)
    questions = _transform_data(data)
    response = QuestionPostResponse()
    response.data = questions
    return response
