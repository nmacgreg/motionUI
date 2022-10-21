# MotionUI - a WebUI for Reviewing Surveillance Video Clips

* This webapp sits on a server hosting files written by "motion". 
* The idea is to make it easy to review the collected footage, with features like queueing the ones you haven't seen, and allowing you to tag interesting videos. 

<hr>
##User Guide: 

# Take #1

* Setup, in Dev: 
    * In ~/dev/motionUI/
    * Use the VirtualEnvironment I set up: `pipenv shell`
    * Use this to control where this software will search for files: `export VIDEOPATH="/home/nmacgreg/Videos/Surveillance"`
    * Gotta set $baseURI ?  `export baseURI="http://localhost:8080/"`
* Run the script: `python grokFiles.py`

## Take #2

* Start redis in a container: `podman run -d --name redis-stack -p 6379:6379 -p 8001:8001 redis/redis-stack:latest`  (personal id), in the background
* Confirm you can connect to it: `podman exec -it --rm redis-stack redis-cli`
* `python dbRedis.py` will query a list, from redis

## Take #3

* One time: you don't need to do this again `pipenv install FastAPI uvicorn jinja2`
* (with redis running as above)
* Download video files to Videos/Surveillance/ (*20220828*)
* Put up httpd : `podman run --rm -v ~/Videos/Surveillance:/usr/local/apache2/htdocs:z -p 8080:80 httpd:2.4` (again, personal ID)
    * Notice: this will eat a terminal; stops easily
* Let's put that new 'main.py' to work:  `uvicorn main:app --reload` in Dev, anyway
* Now simply visit: [http://127.0.0.1:8000/review?video_file=2-02-20220828220249.mp4](http://127.0.0.1:8000/review?video_file=2-02-20220828220249.mp4)
* ... and it works!
* Added a route to the API, to remove the head of the list... can it return the template loaded with the next video
* We added a button to the template, to "mark as reviewed", pointing at the route abov
    * Yes, that button also queries from redis & auto-loads the *next video* in the template?
* I rolled out Redis on Josie, in Production
    * I added a new role to the householdIoT Ansible tree, "redis"
    * I modified the "automation.yml" playbook, to include the new "redis" role
    * I played this new role against Josie
    * I tested rebooting Josie - does redis come up at boot time? 
        * No!  I tried adding "restart_policy: always" to the playbook, played it again, and rebooted again.  No joy!
        * On josie, I issued, `podman start redis --restart=always`, but I did not reboot it 
* I added a route to the API, to tag a named file (didn't check if the file exists)
* To Do: 
    * In  add_tag(), check whether the filename exists, over on melody!
    * Add a button to the template, to add a tag, pointed at the route above. 
    * Add a route to the API, to add a new file to the queue for needing review
        * Test it with a web-browser, or curl
        * Could this be the same as the code above?
    * Add a route that gets a list of all possible tags
    * Clean-up; portability
* To do, in Production:
    * Re-write main.py to be environment sensitive
        * When in Dev environment, refer to http://localhost/<video_file> ...
        * When in Prod environment, refer to http://melody/<video_file> ...
        * I think this means, use a .env file
    * Roll out our new code, on Josie, for real!
    * Add monitoring of redis (josie)
    * Roll out the httpd container on melody; add monitoring of httpd container on melody; make sure it's only bound internally!
    * Change the configuration of "motion" on archie to call a script each time an event ends (just curl the API, with the name of the new file)
    * Error handling: what if the file doesn't exist, on httpd
    * Rate-limiting the API?
    * Monitoring ?  Can we add an API route No-Op for Nagios?
    * Decorate our template to indicate what tags have been applied to the current file
    * Rework the template to display a list of files (and their tags?)
    * Figure out why redis won't restart at boot time, on Josie
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

## Oct 16-

* I touched up docco above, recovering what Cameron and I had worked on, thru August & early Sept. Got Dev working again!
* In Prod:
    * I found householdIoT/roles/redis/ mostly ready
        * I added a stanza to open the Redis port, 6379, through the firewall
        * I played the playbook against Josie
            * I can telnet to josie 6379 :)
            * But I can also hit [http://josie:8001](http://josie:8001), what's up?  Firewall is messed up, please review!
* Follow up on efforts to read from a .env file
    * I was unable to `pipenv install dotenv`; don't understand why
    * I commented out the line that imports, anther that tries to use it

## Follow up on the Dockerfile so far

* I manually created requirements.txt, using `pipenv requirements  > requirements.txt`
* I was able to build it :)  `podman build -t motionui .`
* I used this to login to DockerHub: `podman login` (fished pw from browser)
* But I can't push it

```
motionUI[nmacgreg@veronica motionUI]$ podman push motionui
Getting image source signatures
Error: trying to reuse blob sha256:fe7b1e9bf7922fbc22281bcc6b4f5ac8f1a7b4278929880940978c42fc9d0229 at destination: checking whether a blob sha256:fe7b1e9bf7922fbc22281bcc6b4f5ac8f1a7b4278929880940978c42fc9d0229 exists in docker.io/library/motionui: errors:
denied: requested access to the resource is denied
error parsing HTTP 401 response body: unexpected end of JSON input: ""
```

* OH!  I see, gotta build it with an appropriate tag: `podman build -t docker.io/nmacgreg/motionui .`
* NOPE!  I still can't push that: 

```
motionUI[nmacgreg@veronica motionUI]$ podman push docker.io/nmacgreg/motionui:latest
Getting image source signatures
Error: trying to reuse blob sha256:fe7b1e9bf7922fbc22281bcc6b4f5ac8f1a7b4278929880940978c42fc9d0229 at destination: checking whether a blob sha256:fe7b1e9bf7922fbc22281bcc6b4f5ac8f1a7b4278929880940978c42fc9d0229 exists in docker.io/nmacgreg/motionui: errors:
denied: requested access to the resource is denied
error parsing HTTP 401 response body: unexpected end of JSON input: ""
```

* OHHHHH! Gotta login like this: `podman login docker.io`
* Now I can push: 

```
motionUI[nmacgreg@veronica motionUI]$ podman push docker.io/nmacgreg/motionui:latest
Getting image source signatures
Copying blob 7201e4b9e003 done  
Copying blob 5dd127d33dc2 skipped: already exists  
Copying blob 35bc346c6a37 skipped: already exists  
Copying blob fe7b1e9bf792 skipped: already exists  
Copying blob 1169b1563e05 skipped: already exists  
Copying blob 2596b49d88aa skipped: already exists  
Copying blob b1893817f345 done  
Copying blob dbf9ac308745 done  
Copying blob e14614e9c64b done  
Copying blob 124157c2b63a done  
Copying blob 155bb3f52c84 done  
Copying blob e7b1009a1195 done  
Copying config 12b0d4ff22 done  
Writing manifest to image destination
Storing signatures
```

## Running motionui on Josie...as a container, under Podman

* Create a new householdIoT/roles/motionUI/ playbook, to run motionUI as a container (simple, copied from redis)
* I played it -- it works!
* However, on josie, it says "uvicorn: not found" 
* I confirmed "unicorn" is found in requirements.txt...? Is it just the path? 
* Oh, I readjusted the Dockerfile to use "pipenv" instead of pip, and to use the same path as in dev, but that failed to build:

```
...snip... 
PermissionError: [Errno 13] Permission denied: '/home/motionui/motionUI/.__atomic-write3qg8pruh'
Error: error building at STEP "RUN /home/motionui/.local/bin/pipenv install  --deploy": error while running runtime: exit status 1
```

* I removed motionui userid, ran it as root; back to "uvicorn: not found"
* I removed pipenv, replaced it with bare "pip" ... because it seems pipenv is dead! (dang, since 2020)
* FRUSTRATED with inability to solve this, I thought to replace `uvicorn` entrypoint with /bin/bash & run that in dev... 
* I tried directly `pip install uvicorn`, but that just told me it was already installed

```
Requirement already satisfied: uvicorn in /usr/local/lib/python3.10/site-packages (0.18.3)
```

## one step forward

* I changed the Dockerfile so the last command was just sleep 600
* Then I was able to get a shell in it, with   `podman exec -it competent_poitras /bin/bash`
* /usr/local/bin/uvicorn! At last!
* OK, so I added that... and it worked, sorta
* ... but now python is crashing, printing a "connection failed" error to redis
* OK, I guess that makes sense, I'm not running redis... 
* ? Do Redis and motionUI need to run in the same pod, then? 
* ... and, we're sorta back in the same conundrum: I was trying to build a .env file, and code to import it, which would make it much easier to configure the stuff inside the container.