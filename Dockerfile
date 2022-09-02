# https://pythonspeed.com/articles/base-image-python-docker-images/
FROM python:3.10-slim-bullseye

RUN useradd motionui --create-home
RUN mkdir /home/motionui/motionUI
RUN mkdir /home/motionui/motionUI/templates
USER motionui
WORKDIR /home/motionui/motionUI
COPY main.py main.py
COPY requirements.txt requirements.txt
COPY templates/* templates/

RUN pip install -r requirements.txt

EXPOSE 8000

# https://www.uvicorn.org/#running-with-gunicorn 
ENTRYPOINT uvicorn main:app
