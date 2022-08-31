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
* To Do: 
    * Add a route to the API, to remove the head of the list... can it return the template loaded with the next video
        * Add a button to the template, to "mark as reviewed", pointing at the route above
        * Can that button also auto-load the *next video* in the template?
    * Add a route to the API, to tag the current file (?)
        * Add a button to the template, to add a tag, pointed at the route above. 
    * Add a route to the API, to add a new file to the queue for needing review
        * Test it with a web-browser, or curl
    * Add a route that gets a list of all possible tags
    * Clean-up; portability
* To do, in Production:
    * Roll out the httpd thingy on melody
    * Re-write main.py to use melody...
    * Roll out Redis on Josie, for real
    * Roll out our new code, on Josie, for real!
    * Change the configuration of "motion" on archie to call a script each time an event ends (just curl the API, with the name of the new file)
    * Error handling: what if the file doesn't exist, on httpd
    * Rate-limiting the API?
    * Monitoring ?  Can we add an API route No-Op for Nagios?
* Next round of features:
    * FIX "motion" configuration with a mask to reduce false-positives: no more flowers waving in the wind
    * We already have a route for adding tags to a video...  Cameron envisioned using OpenCV to examine the list of videos, and apply a tag if a human is spotted in the video
    * Can OpenCV spot any other kinds of things?  What else can OpenCV recognize?  Packages left on the step?
    * Can we leverage "motion"'s { start-of-event, end-of-event } features to notify the web-client that action is happening *right now*? 
        * Notification? 
        * Link to open VLC?
        * Announce to Mycroft? 
        * Send an email?  Push-notification to a phone?
    * Move "motion" to melody or josie, for better video output, performance: GPU (leverage container?)
