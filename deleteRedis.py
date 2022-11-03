import redis
key="FilesToReview"
r = redis.Redis(host='josie')
print("The length of the list: ", r.llen(key))
r.lpop(key, r.llen(key))
