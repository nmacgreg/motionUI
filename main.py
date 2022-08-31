import redis

from fastapi import FastAPI, HTTPException
from fastapi.templating import Jinja2Templates

r = redis.Redis()

app = FastAPI()

#########################################################################################
@app.get("/")
async def root():
    """This function merely returns a Hello World dict"""
    return {"message": "Hello World"}

#########################################################################################
@app.get("/review")
async def root():
    """This function populates a template"""
    return {"message": "Hello World"}


