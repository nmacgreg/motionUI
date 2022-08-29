# To Do - Roadmap

* Prototype with [Clappr video player](https://github.com/clappr)... can we serve a web page that has a video player embedded? 
* Decompose into Microservices = FastAPI
    * grokFiles.py transforms into an API; primarily just get the list of files? 
    * Maybe there's a get-first/ get-next / get-prev, for sequential ordering?
* We need multiple backend services: 
    * retrieve a list of the current files (from file listing)
    * tag server: 
        * query the list of tags already applied to a video
        * add a tag to a video
        * remove a tag from a video
        * remove a video from tagging subsystem (eg because it was deleted)
        * how will this data get represented - could this be [Redis](https://realpython.com/python-redis/)
* Docker-compose could put up Redis, the FastAPI backend for files, ... could we do it all with one template served by FastAPI? 

# A vision of UI flow

* At first login, you see a prioritized queue of all the videos to play, with the chronologically oldest one ready to play
* Maybe there's a button, because you're here because something *just* happened, and you'd like to review it
* Youtube "playlist" style? Does the embedded player support this kind of scheme? Autoplay - you can just play all of them, in order; sleepwalk thru them all
* Maybe side-by-side video players, one for each camera? 
* Maybe the top-viewer is frozen, and the videos are listed down below, and you just select which one to play
* A list of all possible existing tags appears by the video. Click on whatever is appropriate, while the video plays, or not
* Channels? Maybe that doesn't apply
 
# Still designing the application in my head

* Maybe all the data lives in Redis, we don't look at files? 
* A component on archie or melody performs maintenance, adding new vids, deleting old vids, when the files change?  Maybe that's an API, protecting Redis' weak security?

# Alternate:

* "file serving" component on melody just indexes the available files - maybe that's a zero-config webserver? 
    * let's try this with podman!
* redis stores all the data about tagging
* a FastAPI service unifies the two, painting a single from a template :)
