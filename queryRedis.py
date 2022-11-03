import redis

r = redis.Redis(host='josie')
print("The top 3 entries: ", r.lrange("FilesToReview", 0, 2))
print("The length of the list: ", r.llen("FilesToReview"))
