import redis


HOST="localhost"
PORT=6379
DB=0

redis_ref = redis.Redis(host=HOST, port=PORT,db=DB)

def set_attribute(key,value):
    redis_ref.set(key,value)

def get_attribute(key):
    return redis_ref.get(key)

def delete_attribute(key):
    redis_ref.delete(key)