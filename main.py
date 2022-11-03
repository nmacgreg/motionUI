import redis
import os

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

load_dotenv()
baseURI = str(os.getenv('baseURI'))
redisHost = str(os.getenv('redisHost'))

r = redis.Redis(host=redisHost)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

#########################################################################################
@app.get("/")
async def root(request: Request):
    """This function queries the top of the Redis queue, and uses the URL found there to feed a video into the player """
    files = r.lrange("FilesToReview", 0, 2)
    return templates.TemplateResponse("reviewVideos.html", {"request": request, "video_URI": files[0].decode('UTF-8')})

#########################################################################################
@app.get("/review", response_class=HTMLResponse)
async def review_video(request: Request, video_file: str):
    """This function populates a template with the filename of the video"""
    #video_URI = baseURI + video_file # canned example
    video_URI = video_file # canned example
    return templates.TemplateResponse("reviewVideos.html", {"request": request, "video_URI": video_URI})

#########################################################################################
@app.get("/Finished", response_class=HTMLResponse)
async def finished_review(request: Request):
    """This function first lpops the list in redis, queries the next file in redis, and populates a template with the filename of the video"""
    r.lpop("FilesToReview")
    video_file = r.lrange ("FilesToReview", 0, 1)
    #video_URI = baseURI + video_file[0].decode('UTF-8') # 
    video_URI = video_file[0].decode('UTF-8') # 
    return templates.TemplateResponse("reviewVideos.html", {"request": request, "video_URI": video_URI})

#########################################################################################
@app.get("/add_tag", response_class=HTMLResponse)
async def add_tag(request: Request, video_file: str, tag: str):
    """This function adds a tag to a filename"""
    r.rpush(tag, video_file)
    video_URI = baseURI + video_file
    return templates.TemplateResponse("reviewVideos.html", {"request": request, "video_URI": video_URI})
