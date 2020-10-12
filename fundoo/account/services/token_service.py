import jwt
from account import redis
import datetime
from util.status import response_code



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

def refresh_token(token):
    key = "secret"
    try:
        decode = jwt.decode(token, 'secret')
    except jwt.DecodeError:
        return {"code":306,"msg":response_code(306)}
    except jwt.ExpiredSignatureError:
        return {"code":304,"msg":response_code(304)}
    username = decode.get('username')
    payload = {"username":username}
    
    payload["exp"] = datetime.datetime.utcnow() + datetime.timedelta(days=1)
    new_token = jwt.encode(payload, key).decode('utf-8')
    print(new_token)
    redis.set_attribute(username,new_token)
    return {"token":new_token, "code":200, "msg":response_code[200]}