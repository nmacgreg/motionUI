#!/usr/bin/python

import os 


# read the diretories containing the videos to be processed, from an Environment Variable
directories=os.environ["VIDEOPATH"]  # might be a comma-separated list

if not directories: 
    exit

# Parse the comma-separated list: 
for dir in directories.split(','): 

    if os.path.isdir(dir):
        # get a listing of the directory
        files = os.listdir(dir)
        
        for file in files:
            print(file)



