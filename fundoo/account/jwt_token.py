import jwt


def generate_token(payload):
    key = "secret"
    token = jwt.encode(payload, key).decode('utf-8')
    return token
