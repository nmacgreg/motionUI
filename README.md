# MotionUI - a WebUI for Reviewing Surveillance Video Clips

* This webapp sits on a server hosting files written by "motion". 
* The idea is to make it easy to review the collected footage, with features like queueing the ones you haven't seen, and allowing you to tag interesting videos. 

<hr>
##User Guide: 

# Take #1

* Setup: 
    * Use this environment variable to control where this software will search for files: `export VIDEOPATH="/home/nmacgreg/Videos/Surveillance"`
* Run the script: `python grokFiles.py`

## Take #2

* Start redis in a container: `podman run -d --name redis-stack -p 6379:6379 -p 8001:8001 redis/redis-stack:latest`  (personal id)
* Confirm you can connect to it: `podman exec -it --rm redis-stack redis-cli`
* `python dbRedis.py` will query a list, from redis

## Take #3

* One time: you don't need to do this? `pipenv install FastAPI uvicorn jinja2`
* (with redis running as above)
* Download video files to Videos/Surveillance/ (*20220828*)
* Put up httpd as simplest web service: `podman run --rm -v ~/Videos/Surveillance:/usr/local/apache2/htdocs:z -p 8080:80 httpd:2.4` (again, personal ID)
* Let's put that new 'main.py' to work:  `uvicorn main:app --reload` in Dev, anyway
* Now simply visit: http://127.0.0.1:8000/review?video_file=2-02-20220828220249.mp4
* ... and it works!
