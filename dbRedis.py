import redis

r = redis.Redis()

print(r.ping())

# Let's manually construct some data
data = {
        "2-01-20220828220133.mp4": {
            "reviewed": "no"
        }, 
        "2-02-20220828220249.mp4": {
            "reviewed": "no",
            "humans": "no"
        }
}

AllFiles = [ "2-01-20220828220133.mp4", "2-02-20220828220249.mp4", "2-03-20220828220352.mp4", "2-04-20220828220453.mp4", "2-05-20220828221854.mp4", "2-06-20220828222648.mp4", "2-07-20220828223149.mp4", 
             "2-08-20220828223313.mp4", "2-09-20220828223528.mp4", "2-10-20220828231126.mp4", "2-11-20220828231328.mp4", "2-12-20220828232618.mp4", "2-13-20220828232950.mp4" ]


# Can we store the AllFiles list into Redis? 
# Note: Redis lists are implemented as linked lists, not arrays. So, push & pop operations are fast. But indexing down the list is O(n) slow! Querying whether the list contains an entry is slow. 
# You can LPUSH (head) or RPUSH (tail) when adding elements. 
# You can LPOP from the head, or LPOP from the tail
# With LRANGE <start-from> <count>, you can start from anywhere in the list and get then next <count> elements; "LRANGE 0 9" gets the first 10 videos!
r.rpush("FilesToReview", *AllFiles)

print(r.lrange("FilesToReview", 0, 2))


# Redis keys also have a TTL. If we use the filenames as the keys, we could set them to expire at the same time the cron job will delete them.  
# Meaning, we don't need to modify the cron job that deletes files.  The Redis entries will automatically go away!



