import jwt
from rest_framework import authentication
from rest_framework.authentication import exceptions
from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)


class JWTAuthentication(authentication.BaseAuthentication):

    def authenticate(self, request):
        auth_data = authentication.get_authorization_header(request)

        if not auth_data:
            return None

        prefix, token = auth_data.decode('utf-8').split(' ')
        logger.info(auth_data)
        try:
            payload = jwt.decode(token, 'secret')

            user = User.objects.get(username = payload["username"])
            return (user, token)
        except jwt.DecodeError:
            raise exceptions.APIException('Invalid Token')
        except jwt.ExpiredSignatureError:
            raise exceptions.APIException('Token expired')


        return super().authenticate(request)