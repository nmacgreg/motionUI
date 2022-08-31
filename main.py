import redis

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

r = redis.Redis()

app = FastAPI()
templates = Jinja2Templates(directory="templates")

#########################################################################################
@app.get("/")
async def root():
    """This function merely returns a Hello World dict"""
    return {"message": "Hello World"}

#########################################################################################
@app.get("/review", response_class=HTMLResponse)
async def review_video(request: Request, video_URI: str):
    """This function populates a template with the filename of the video"""
    video_URI = "2-13-20220828232950.mp4" # canned example
    return templates.TemplateResponse("reviewVideos.html", {"request": request, "video_URI": video_URI})

