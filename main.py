import redis
import os
import sys

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

load_dotenv()
baseURI = str(os.getenv('baseURI'))
redisHost = str(os.getenv('redisHost'))

try: 
    r = redis.Redis(host=redisHost)
except redis.exceptions.ConnectionError: 
     raise HTTPException(status_code=404, detail=f"Initial connection to Redis failed, host = {redisHost}")
RedisKey="FilesToReview"

app = FastAPI()
templates = Jinja2Templates(directory="templates")

#########################################################################################
@app.get("/")
async def root(request: Request):
    """This function queries the top of the Redis queue, and uses the URL found there to feed a video into the player """
    try: 
        files = r.lrange(RedisKey, 0, 2)
    except redis.exceptions.ConnectionError: 
        raise HTTPException(status_code=404, detail=f"Redis query failed, host = {redisHost}")

    if files:
        return templates.TemplateResponse("reviewVideos.html", {"request": request, "video_URI": files[0].decode('UTF-8'), "videos_Remaining": r.llen(RedisKey)})
    else: 
        return templates.TemplateResponse("allDone.html", {"request": request })

#########################################################################################
@app.get("/review", response_class=HTMLResponse)
async def review_video(request: Request, video_file: str):
    """This function populates a template with the filename of the video"""
    #video_URI = baseURI + video_file # canned example
    video_URI = video_file # canned example
    return templates.TemplateResponse("reviewVideos.html", {"request": request, "video_URI": video_URI, "videos_Remaining": r.llen(RedisKey)})

#########################################################################################
@app.get("/Finished", response_class=HTMLResponse)
async def finished_review(request: Request):
    """This function first lpops the list in redis, queries the next file in redis, and populates a template with the filename of the video"""
    try: 
        r.lpop(RedisKey)
    except redis.exceptions.ConnectionError: 
        raise HTTPException(status_code=404, detail=f"Redis query failed, host = {redisHost}")

    video_file = r.lrange (RedisKey, 0, 1)
    if video_file: 
        video_URI = video_file[0].decode('UTF-8') # 
        return templates.TemplateResponse("reviewVideos.html", {"request": request, "video_URI": video_URI, "videos_Remaining": r.llen(RedisKey)})
    else: 
        return RedirectResponse(url='/')

#########################################################################################
@app.get("/add_tag", response_class=HTMLResponse)
async def add_tag(request: Request, video_file: str, tag: str):
    """This function adds a tag to a filename"""
    try:
        r.rpush(tag, video_file)
    except redis.exceptions.ConnectionError: 
        raise HTTPException(status_code=404, detail=f"Redis rpush failed, host = {redisHost}")
    
    video_URI = baseURI + video_file
    return templates.TemplateResponse("reviewVideos.html", {"request": request, "video_URI": video_URI, "videos_Remaining": r.llen(RedisKey)})
