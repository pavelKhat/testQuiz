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


def get_questions_from_api(question_count: int) -> list[QuestionsModel]:
    """Function that loads questions form external API."""
    url = API_URL_TEMPLATE.format(question_count)
    try:
        response = requests.get(url).json()
    except requests.HTTPError as error:
        raise HTTPException(400, detail=f"{error.request} was unsuccesseful! {error}")
    return response


@app.post('/questions', response_model=QuestionPostResponse)
def post_questions(request: QuestionsPostRequest):
    """Endpoint for Questions post request, """
    questions = get_questions_from_api(request.questions_num)

    return questions
