# https://pythonspeed.com/articles/base-image-python-docker-images/
# https://jonathanmeier.io/using-pipenv-with-docker/
FROM python:3.10-slim-bullseye

RUN useradd motionui --create-home
RUN mkdir /root/motionUI
RUN mkdir /root/motionUI/templates
#USER motionui
WORKDIR /root/motionUI
COPY requirements.txt requirements.txt
COPY main.py main.py
COPY templates/* templates/

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir uvicorn

EXPOSE 8000

# https://www.uvicorn.org/#running-with-gunicorn 
#ENTRYPOINT /usr/local/bin/uvicorn main:app
#CMD python -m uvicorn main:app --host 0.0.0.0 --port 80
CMD /usr/local/bin/uvicorn main:app
