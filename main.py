import redis

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

r = redis.Redis()
files = r.lrange("FilesToReview", 0, 2)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

#########################################################################################
@app.get("/")
async def root():
    """This function merely returns a Hello World dict"""
    return {"message": "The first file is: " + files[0].decode('UTF-8')}

#########################################################################################
@app.get("/review", response_class=HTMLResponse)
async def review_video(request: Request, video_file: str):
    """This function populates a template with the filename of the video"""
    video_URI = "http://localhost:8080/" + video_file # canned example
    return templates.TemplateResponse("reviewVideos.html", {"request": request, "video_URI": video_URI})

#########################################################################################
@app.get("/Finished", response_class=HTMLResponse)
async def finished_review(request: Request):
    """This function first lpops the list in redis, queries the next file in redis, and populates a template with the filename of the video"""
    r.lpop("FilesToReview")
    video_file= r.lrange ("FilesToReview", 0, 1)
    video_URI = "http://localhost:8080/" + video_file[0].decode('UTF-8') # 
    return templates.TemplateResponse("reviewVideos.html", {"request": request, "video_URI": video_URI})

