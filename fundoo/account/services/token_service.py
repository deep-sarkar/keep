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
        token_key = username +'_token_key'
        token = redis.get_attribute(token_key)
        jwt.decode(token,'secret')
    except Exception as e:
        pass
    if token == None:
        payload["exp"] = datetime.datetime.utcnow() + datetime.timedelta(days=3)
        token = jwt.encode(payload, key).decode('utf-8')
        token_key = username +'_token_key'
        print(token_key)
        redis.set_attribute(token_key,token)
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
    token_key = username +'_token_key'
    redis.set_attribute(token_key,new_token)
    return {"token":new_token, "code":200, "msg":response_code[200]}