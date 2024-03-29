# MotionUI - a WebUI for Reviewing Surveillance Video Clips

* This webapp is designed to make it easy to review video footage collected by "motion", with features like queueing the ones you haven't seen, and allowing you to tag interesting videos. 

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

## Oct 16, 2022 - AV-Club & OpenCV

* I'm here because I signed up to cover #AV-Club this week, including a demo of the OpenCV work I'd spoken about in Sept
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

## One step forward

* I changed the Dockerfile so the last command was just sleep 600
* Then I was able to get a shell in it, with   `podman exec -it competent_poitras /bin/bash`
* /usr/local/bin/uvicorn! At last!
* OK, so I added that... and it worked, sorta
* ... but now python is crashing, printing a "connection failed" error to redis
* OK, I guess that makes sense, I'm not running redis... 
* ? Do Redis and motionUI need to run in the same pod, then? 
* ... and, we're sorta back in the same conundrum: I was trying to build a .env file, and code to import it, which would make it much easier to configure the stuff inside the container.

## Dotenv solved

* I just followed [the instructions](https://pypi.org/project/python-dotenv/)
* `pipenv install python-dotenv` & uncommented those 2 lines in main.py
* I created a .env with those 2 vars in it, VIDEOPATH & baseURI
* ... of course, you gotta have httpd and redis running!
* Maybe I need a docker-compose.yml for dev?

## Can't connect to redis

* `podman run docker.io/nmacgreg/motionui:latest` since you built it locally
* ... but `redis.exceptions.ConnectionError: Error 111 connecting to localhost:6379. Connection refused.`... even though Redis is up, in another container.
* And I'm pretty sure that's by design! Containers are on separate networks by default - we'd have to create a network, and assign them both to it, so they can talk.
* And that's where the concept of Pods comes in -- we need to put these apps into the same pod, so they can talk together
* !But -- REDIS is avaialble on "josie:6379"! --SUGGEST A CONNECTION STRING FOR REDIS THAT DOESN'T ASSUME "localhost" !!!
* (Redis is available so a proposed script on Archie can update redis when new video files are created!)
* So, I : 
    * Added an environment var to .env
    * Edited main.py, reading the environment var, using it to set a variable, and using that to set the host for redis
    * I tested it in Dev: works fine
    * I rebuilt the image & pushed it to dockerhub
* On josie: 
    * I pulled the updated image
    * I've never used a .env file here before! How does that work?
    * `[root@josie ~]# podman run  --env-file=./env-for-motionUI motionui:latest` It works! [Thanks](https://stackoverflow.com/questions/72154504/podman-exec-env-file-seemingly-not-working)
    * And there's room to add credentials, if that ever becomes a thing!

## Mapping a port for motionui on Josie

* Now, gotta map a port on josie, 'cos I can't connect to it
* `[root@josie ~]# podman run -d  -p 8000:8000 --env-file=./env-for-motionUI motionui:latest`
* (already got that port open through the firewall)
* I can see it's mapped: 

```
[root@josie ~]# ss -tna | grep 8000
LISTEN     0      4096               0.0.0.0:8000             0.0.0.0:* 
```

* But I can't connect to it. Not with a browser.  Not with telnet. Not locally on Josie.  Not remotely. DANG.
* `podman logs <id>` shows me NOTHING. Hmph.
* I tried starting it in dev on veronica, but it won't run here

## About that Demo

* In summary, I didn't get MotionUI working in time for the demo...
* However, in preparation for the demo, I did play around with the OpenCV for several hours
    * It was quite laggy on veronica, so I proceeded to try to get it running on Jughead... And I did, but it wasn't any better
    * (by laggy, I mean, it would lose half a second, per second.  After 60 seconds, it's 30 seconds behind!)
    * I modified it to use 640x480 stream on ".../channel/102", which improved the performance somewhat, but not dramatically
* I demo'd "fd2.py" for Omar in the #AV-Club Oct 21
* It wasn't until after the demo that I realized it was *recording* each video to a file, output.avi!
    * The file is playable in VLC or the default movieplayer app
    * ...but, I don't actually want that feature, and wouldn't that be a drag on performance? 
    * So, I commented out those parts that open the file, write to the file, and close the file
    * It still works (!)
    * After 60 seconds of capture, it's only 45 seconds behind!
* (I didn't realize until afterwards, veronica is a Ryzen-5 with 8 cores, and it still keeps them all busy, maybe a little less now, maybe 85% - this doesn't feel like it's GPU-accelerated; nor on jughead)

## Digging into fd2.py & OpenCV

* Actually reading the code even more...
* [OpenCV-python docs](https://pypi.org/project/opencv-python/)
* This explicitly says, right at the top, "Pre-built *CPU-only* OpenCV packages for Python", so yeah, no GPU acceleration, duh
* ! It also says there is a smaller package set for running it headless !
* If I comment-out the `cv2.rectangle` part, 
    * it stops drawing the rectangles in the video (but, performance doesn't improve)
    * and if I replace that with just printing "human detected", then I get fun output!
* If I comment-out the `cv2.imshow` part, it stops rendering the video onscreen (but again, no improvement in performance), and just spits out "human detected"

## peopleDetector.py

* Ejecting legacy; concentrate on goals
* Goal: fit this into the imagined framework!
    * A video-file will appear on the NFS drive, as the start-event...
    * Feed the file into the HOG PeopleDetector feature of OpenCV
    * Obtain a confidence rating describing how many times it detected a person for each video file
    * Use the confidence rating as a low-bypass filter, to reduce false-positives
    * Take action -- tag videos in Redis with "Human Detected" and the confidence rating!
* How about counting the total number of frames, and then number of frames containing a human, and calculating a percentage?
* YES, removed all the waitKey & window stuff: still works
* Yes, it will just accept a local filename, rather than an `rtsp://...` URI -- first tried Kenzie's Acro vid!
* Yes, there's a line that converts the video frame to greyscale, but then doesn't use it.  
    * I swapped it in, in place of "frame"... and it works, both for detectection, and for output
    * But, no, it offers no speed increase that I can tell; no CPU reduction
* Idea: this screams out to be implemented as just another service: 
    * you feed me a URL, I'll output a confidence rating that this video contains a human!
    * maybe an option: also output a video with the rectangles overlayed, for review, for diagnosis
* Idea: what happens if we try to process actual videos created by "Motion" from ~/Videos/Surveillance/? 
    * Oh! Converting it to 640x480 from 2688x1520 (thanks, VLC) results in tall, skinny humans...
    * Better: 640x362 preserves the aspect ratio!
* ?How long does to take to process a 42-second video with peopleDetector.py?  
    * 51 seconds in colour, native resolution
    * 44 seconds @ 640x362
    * 44 seconds in grayscale (sooo... no difference!)
    * 44 seconds if I remove the numpy jazz we don't need (no difference)
* Idea: Yeah, we really ought to build this natively so it'll do GPU acceleration
    * [Blog says 8x speedup on GPU for HOG](https://imaginghub.com/blog/12-using-opencv-for-gpu-hardware-on-linux) (2017) and demonstrates how to compile it yourself, on Ubuntu
* Notice: processing every file from Motion ends with an error :

```
cv2.error: OpenCV(4.3.0) /builddir/build/BUILD/opencv-4.3.0/modules/imgproc/src/color.cpp:182: error: (-215:Assertion failed) !_src.empty() in function 'cvtColor'
--or-- 
cv2.error: OpenCV(4.3.0) /builddir/build/BUILD/opencv-4.3.0/modules/imgproc/src/resize.cpp:3929: error: (-215:Assertion failed) !ssize.empty() in function 'resize'
```

* ... as if Motion is not obeying some file-format rule at the end... last frame is empty, or something?
    * VLC reports 1786 frames 
    * I added error handling to the resize & cvtColor operations... I tried using "next", but had to use "break" or it would never end
    * But peopleDetector reports 76 frames before it exists, only 16 of those contain humans.  Hmmmmm

## So, it's a web service, huh? 

* FastAPI front-end
* parameter gives the URI for the video to process
* return value is just

## Other neato features to explore, later...:

* Hey! OpenCV has a [background subtraction][https://docs.opencv.org/4.x/d1/dc5/tutorial_background_subtraction.html] feature, which highlights moving objects, when using a static camera -- this is worth investigating!
* 

## Halloween: Firing a Script on Archie from Motion

* This script doesn't exist yet
* But it's going to look a lot like dbRedis.py
* Let's get started -- can you ping/pong Redis from Archie?
* Prep Archie, building mini-dev environment:
    * Install git, then python3-pip (as root, with apt)
    * In my home dir...
        *  make ~/dev/ & go there
        * clone motionUI.git
        * `pip install pipenv`
        * Appended to .bashrc: `export PATH=/home/nmacgreg/.local/bin:$PATH `
        * logout/login
        * `nmacgreg@archie:~/dev/motionUI $ pip install --user -r requirements .txt` to install all the modules (long, on Pi)
        * `pipenv shell` FAILS, we have python 3.9, need 3.10
        * ... but I thought pip managed the version of python?  No, we need "pyenv" for that. And a development environment!  It *builds pythons from source!*  Uh... "pyenv" is too much!
* Hmmm, can we just get away with `pip install redis`? 
    * (it's already installed, probably thanks to pipenv...? )
    * I edited dbRedis.py, keeping only the connection to Redis and the ping; added "... host='josie'" parameter.  But that fails - all attempts to run `python dbRedis.py` just hang forever, and when you hit cntl-C, you get a Redis connection error
    * I can telnet to josie on 6379, both from archie, and from veronica
    * Mangling dbRedis.py in the same way, on veronica, also fails to connect to Redis!
    * ARGH!
    * AH!! I restarted Redis on Josie! Veronica works!
    * And it works on Archie!
* Research: 
    * [on-movie-end scripting in "motion"](https://motion-project.github.io/motion_config.html#OptDetail_Scripts)
    * [motion's 'conversion specifiers'](https://motion-project.github.io/motion_config.html#conversion_specifiers), just use %f to get the filename specified on the commandline!
* Building Minimum-Viable, "on-movie-end.py"
    * hardcoded "josie" as redis server
    * Keep the connection to redis (failed adding try/except blocks)
    * Add code to process argv as a list of filenames for the video just written
    * Use a "list comprehension" to replace the /var/lib/motion/ path prefix, with the URL to melody
    * ...and then use lpush to stack plates into redis - it's *simple*!  Just glue!
* Configuring "motion" to use that:
    * Yes, it really is that simple
    * Ah, but watching the log, it fails when the "redis" module can't be found
    * `pip install redis` was local to my account, but "motion" runs as userid "motion", reports an error loading module
    * Resolved `apt install python3-redis` as root of course - that fixed it
    * Hint: `journalctl -f -u motion`
    * "Skeletony" waving in the wind is giving me a lot of events to work with!
*  Testing: 
    * Wrote new "listPython.py" to dump the contents of the Redis data structure
    * Hmm, it doesn't look like it's working
    * Ah, there's confusion around which code is adding the http://10.0.0.1/ prefix (both are, it's duplicated)
    * It's working!
* I wrote new queryRedis.py, to output the total number of records in Redis' "FilesToReview" struct... wait, over 11,000 records? It seems we're adding new files almost every minute, thanks to Skele-tony!
    * Note: restarting Redis on Josie doesn't delete any entries
    * I wrote deleteRedis.py, which lpops the entire contents of the "FilesToReview" key, and used it
    * I also deleted all 11,000 files
* New Testing: 
    * Visit [The Home Page](http://127.0.0.1:8000/) and it links you to the first file, but the timestamp is old. 
    * ? Restart uvicorn/main?  Yes, that fixes it.
    * Yes, now the events in the stack are occurring in order by time
    * Yes, I can even see videos from the camera inside the garage, interspersed with the exterior camera! Nice!
* Fixing: The value on the home page is queried at startup & never changes. Fix that.
    * Dead easy - move the line that queries Redis into the "root()" function. Done!
* Fixing: When you visit [The Home Page](http://127.0.0.1:8000/), there's no way to kick off the first review!
    * Also dead simple... 
    * "main()" takes the Request as input
    * ... and it returns the template, stuffed with the first entry queried from Redis!
* Fixing: We need to create a different template, as an action to fall back into, when the Redis queue is empty, rather than generating an "Internal Server Error" by using an empty result from the Redis query
    * Added template allDone.html
    * Modified main.py to conditionally call the 'allDone' template, whenever Redis is empty
* Implementing new feature: the "reviewVideos" template could print the Redis queue depth, so we know how many more are to go
    * Adjusted the template
    * Modified main.py to retrieve queue depth & supply it as input to the template, whenever the template it called!
    * Again, dead simple!
* Fixing: When you fall off the end of the video-review-queue on "/Finished", and the queue is empty, could we be redirected back to the home page, so that hitting reload ctrl-R will restart the process of reviewing new vids, when they arrive?
    * I added an import of RedirectResponse
    * Then, at the end of "finished_review()", I called that function with: url="/"  And it works - simple!

# Testing

* Over the course of a couple of days, and with the help of Skele-Tony turning in the wind and generating new videos every few minutes, I was able to do a lot of testing
* This sucker will generate > 400 videos per day
* This was useful: `for a in {1..50}; do curl http://127.0.0.1:8000/Finished? >/dev/null; done` for trimming the queue
* We've got to do something about the source of the videos: "motion"
    * the videos are slow-motion
    * the framerate is awful
    * the thing I actually want -- videos of people -- are almost always filled with "ghost" image, pauses, etc
    * the videos feature dropped frames all over the place! 
    * the journal for motion is filled with: `ffmpeg_set_codec: Low fps. Encoding 5 frames into a 10 frames container.`
    * While Skele-Tony is useful for testing, the count of false-positives is far too high: need a mask!

# To Do: 

* This could use "Next" and "Previous" buttons, to skip the step of lpopping  (But, that means keeping track of where you are in the list)
* Start using gitops for this project
* If you have this running in Dev, and close your laptop, the connection to Redis will probably be invalid, so the first time you push a button in your browser, it'll fail
