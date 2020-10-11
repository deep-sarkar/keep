import jwt
from account import redis
from rest_framework_jwt.settings import api_settings

jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER


def generate_token(payload):
    key = "secret"
    token = jwt.encode(payload, key).decode('utf-8')
    return token

def generate_login_token(user):
    username = user.username
    try:
        token = redis.get_attribute(username)
        jwt.decode(token)
    except Exception as e:
        pass
    if token == None:
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
    return token
