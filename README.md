# MotionUI - a WebUI for Reviewing Surveillance Video Clips

* This webapp sits on a server hosting files written by "motion". 
* The idea is to make it easy to review the collected footage, with features like queueing the ones you haven't seen, and allowing you to tag interesting videos. 

<hr>
User Guide: 
* Setup: 
    * Use this environment variable to control where this software will search for files: `export VIDEOPATH="/home/nmacgreg/Videos/Surveillance"`
* Run the script: `python grokFiles.py`

## Take #2

* Start redis in a container
* `python dbRedis.py` will query a list, from redis
