FROM python:3.10

WORKDIR /test_app

COPY requirements.txt .

RUN pip3 install --upgrade pip -r requirements.txt

COPY quiz_app .

EXPOSE 8000
