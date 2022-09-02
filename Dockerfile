# https://pythonspeed.com/articles/base-image-python-docker-images/
FROM python:3.10-slim-bullseye

COPY main.py 
COPY requirements.txt
COPY templates/*

RUN pip install -r requirements.txt

# https://www.uvicorn.org/#running-with-gunicorn 
CMD uvicorn main:app
