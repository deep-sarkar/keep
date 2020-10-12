import jwt
from account import redis
import datetime



def generate_token(payload):
    key = "secret"
    payload["exp"] = datetime.datetime.utcnow() + datetime.timedelta(days=1)
    token = jwt.encode(payload, key).decode('utf-8')
    return token

def generate_login_token(payload):
    key = "secret"
    username = payload['username']
    try:
        token = redis.get_attribute(username)
        jwt.decode(token,'secret')
    except Exception as e:
        pass
    if token == None:
        payload["exp"] = datetime.datetime.utcnow() + datetime.timedelta(days=3)
        token = jwt.encode(payload, key).decode('utf-8')
        redis.set_attribute(username,token)
    return token
