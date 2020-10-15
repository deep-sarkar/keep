from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

#import from django
from django.contrib.auth import get_user_model, login, logout, authenticate
from django.core.validators import validate_email
from django.template.loader import render_to_string


#Short url
from django_short_url.models import ShortURL

#import from serializers
from .serializers import (RegistrationSerializer, 
                          LoginSerializer, 
                          ResetPasswordSerializer, 
                          ForgotPasswordSerializer)

#token
from account.services.token_service import generate_token, generate_login_token, refresh_token

#errors
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from .exceptions import UserCreationError, UsernameDoesNotExistsError
                        
from smtplib import SMTPException

#validator
from .validation_function import validate_user_does_not_exists
from account.validate import( validate_registration, 
                              validate_login, 
                              validate_reset_password,
                              validate_change_password
                              )

from account.services.email_services import send_account_activation_mail, send_forgot_password_mail
from account.services.repository import (create_user,
                                          set_new_password)


import jwt

#User model
User = get_user_model()

#redis object
from . import redis

#Static data
from util import static_data
from util.status import response_code

# Decorator
from util.decorator import custom_login_required
from django.utils.decorators import method_decorator

# Cache
from django.core.cache import cache

import logging


class Registration(GenericAPIView):
    serializer_class = RegistrationSerializer
    

    def post(self, request, *args, **kwargs):
        '''
        param request: Http request contains user data
        returns: 201 created or error
        '''
        if request.user.is_authenticated:
            return Response({'code':410,'msg':response_code[410]})
        valid = validate_registration(request)                  #validate request data return msg if error occour
        if valid != None:
            return Response(valid)  #If error occour will return error msg and code
        try:
            create_user(request)                                            #will create user
            send_account_activation_mail(request)                           #Sending account activation mail
        except UserCreationError as e:
            logging.warning(e)
            return Response({'code':e.code,'msg':e.msg})
        except SMTPException as e:
            return Response({'code':301,'msg':response_code[301]})
        return Response({"code":201, "msg":response_code[201]})



class LoginAPIView(GenericAPIView):
    serializer_class = LoginSerializer
        
    def post(self, request, *args, **kwargs):
        '''
        param request: Http request contains login detail
        returns : 200 success and token or error
        '''
        try:
            if request.user.is_authenticated:
                return Response({'code':410,'msg':response_code[410]})
            username = request.data.get('username')
            password = request.data.get('password')
            valid = validate_login(username, password)                                             #validate request data
            if valid != None:
                return Response(valid)                         #If error occour will return error msg and code
            user_obj = authenticate(request, username=username, password=password)
            if user_obj is not None:
                if user_obj.is_active:
                    login(request,user_obj)
                    payload = {"username":username}
                    token = generate_login_token(payload)
                    return Response({'code':200,'msg':response_code[200],'token':token})
                return Response({'code':411,'msg':response_code[411]})
            return Response({"code":416, "msg":response_code[416]})
        except Exception as e:
            logging.warning(e)
            return Response({"code":416, "msg":response_code[416]})

class Logout(GenericAPIView):
    serializer_class = LoginSerializer

    @method_decorator(custom_login_required)
    def get(self, request, *args, **kwargs):
        '''
        param request: Http request contains user detail
        returns: 200 successful
        '''
        try:
            if not request.user.is_authenticated:
                return Response({'code':413, 'msg':response_code[413]})
            cache.clear()
            logout(request)
            return Response({'code':200,'msg':response_code[200]})
        except Exception as e:
            logging.warning(e)
            return Response({"code":416, "msg":response_code[416]})

class ChangePasswordView(GenericAPIView):
    serializer_class = ResetPasswordSerializer

    @method_decorator(custom_login_required)
    def post(self, request, *args, **kwargs):
        '''
        param request: Http request contains password data and confirm data
        returns: 200 successful or error
        '''
        try:
            if not request.user.is_authenticated:
                return Response({'code':413, 'msg':response_code[413]})
            valid = validate_change_password(request)  #validate request data
            if valid != None:
                return Response(valid)   #If error occour will return error msg and code
            username         = request.user.username
            password         = request.data.get('password')
            password_set = set_new_password(username, password)
            if password_set:
                token_key = username +'_token_key'
                redis.delete_attribute(token_key)
                return Response({'code':200,'msg':response_code[200]})
            return Response({'code':416,'msg':response_code[416]})
        except Exception as e:
            logging.warning(e)
            return Response({"code":416, "msg":response_code[416]})
        
class ActivateAccount(GenericAPIView):
    serializer_class = LoginSerializer

    def get(self, request, surl):
        '''
        param request: Http request , surl
        returns : 200 successful or error
        '''
        try:
            token_obj = ShortURL.objects.get(surl=surl)
            token     = token_obj.lurl
            decode    = jwt.decode(token, 'secret')
            username  = decode['username']
            validate_user_does_not_exists(username)
        except jwt.DecodeError:
            return Response({'code':304,'msg':response_code[304]})
        except UsernameDoesNotExistsError as e:
            return Response({'code':e.code, 'msg':e.msg})
        except Exception as e:
            logging.warning(e)
            return Response({'code':409,'msg':response_code[409]})
        user = User.objects.get(username=username)
        if user.is_active:
            return Response({'code':302, 'msg':response_code[302]})
        else:
            user.is_active = True
            user.save()
            return Response({'code':200,'msg':response_code[200]})

class ForgotPasswordView(GenericAPIView):
    serializer_class = ForgotPasswordSerializer

    def post(self, request, *args, **kwargs):
        '''
        param request : Http request cotains email
        return : Send reset mail or error
        '''
        email = request.data.get('email')
        try:
            validate_email(email)
            user = User.objects.filter(email=email)
            username = user.values()[0]['username'] 
            send_forgot_password_mail(request, username)
            return Response({'code':200,'msg':response_code[200]})
        except ValidationError:
            return Response({'code':404,'msg':response_code[404]})
        except IndexError:
            return Response({'code':303,'msg':response_code[303]})          
        except SMTPException:
            return Response({'code':301,'msg':response_code[301]})

class ResetNewPassword(GenericAPIView):
    serializer_class = ResetPasswordSerializer

    def post(self, request, *args, **kwargs):
        try:
            surl= kwargs.get('surl')
            token_obj = ShortURL.objects.get(surl=surl)
        except Exception as e:
            logging.warning(e)
            return Response({'code':409,'msg':response_code[409]})
        token = token_obj.lurl   #get token from token object
        username = validate_reset_password(token,request)
        if type(username) != str:
            return Response(username)   #If error occour will return error msg and code
        password = request.data.get('password')
        password_set = set_new_password(username, password)
        if password_set:
            return Response({'code':200,'msg':response_code[200]})
        return Response({'code':416,'msg':response_code[416]})


class RefreshToken(GenericAPIView):
    serializer_class = ForgotPasswordSerializer


    def post(self, request):
        token = request.data.get('token')
        if token != None:
            token = refresh_token(token)
            return Response(token)
        return Response({'code':416,'msg':response_code[416]})