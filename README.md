# Test Quiz App

This is a simple application used as test task.

It's receive POST requests to collect questions for quiz from external API.

## Installation and Usage

Application use [Docker](https://www.docker.com/) and [docker compose](https://docs.docker.com/compose/) for 
containerization.

[FastAPI](https://fastapi.tiangolo.com/) as web server and [PostgresSQL](https://www.postgresql.org/) as database.

To run application you need download repo, make sure that you have installed Docker and docker-compose.

Navigate to main folder:

```bash
docker-compose up -build
```

Application web server will respond on 8000 port.

Here is 'curl' request example:

```bash
curl -X 'POST' \
  'http://0.0.0.0:8000/questions' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "questions_num": 1
}'
```

And you will receive response like this:

```bash
{
  "id": 40799,
  "question": "1 of the 2 things the DX coding on a roll of film tells your camera",
  "answer": "the speed (and the number of exposures)",
  "created_at": "2022-12-30T18:54:36.353000"
}
```

Exception first request to new service. There will be an information error, that database don't have any records.