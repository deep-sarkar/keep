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
from account.services.token_service import generate_token, generate_login_token

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


class Registration(GenericAPIView):
    serializer_class = RegistrationSerializer
    

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return Response({'code':410,'msg':response_code[410]})
        valid = validate_registration(request)                  #validate request data return msg if error occour
        if valid != None:
            return Response(valid)  #If error occour will return error msg and code
        try:
            create_user(request)                                            #will create user
            send_account_activation_mail(request)                           #Sending account activation mail
        except UserCreationError as e:
            return Response({'code':e.code,'msg':e.msg})
        except SMTPException:
            return Response({'code':301,'msg':response_code[301]})
        return Response({"code":201, "msg":response_code[201]})



class LoginAPIView(GenericAPIView):
    serializer_class = LoginSerializer
        
    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return Response({'code':410,'msg':response_code[410]})
        username = request.data.get('username')
        password = request.data.get('password')
        valid = validate_login(request)                                             #validate request data
        if valid != None:
            return Response(valid)                         #If error occour will return error msg and code
        user_obj = authenticate(request, username=username, password=password)
        if user_obj is not None:
            if user_obj.is_active:
                login(request,user_obj)
                token = generate_login_token(user_obj)
                redis.set_attribute(username,token)
                return Response({'code':200,'msg':response_code[200],'token':token})
            return Response({'code':411,'msg':response_code[411]})
        return Response({'code':412,'msg':response_code[412]})

class Logout(GenericAPIView):
    serializer_class = LoginSerializer

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({'code':413, 'msg':response_code[413]})
        logout(request)
        return Response({'code':200,'msg':response_code[200]})

class ChangePasswordView(GenericAPIView):
    serializer_class = ResetPasswordSerializer

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({'code':413, 'msg':response_code[413]})
        valid = validate_change_password(request)  #validate request data
        if valid != None:
            return Response(valid)   #If error occour will return error msg and code
        username         = request.user.username
        password         = request.data.get('password')
        password_set = set_new_password(username, password)
        if password_set:
            return Response({'code':200,'msg':response_code[200]})
        return Response({'code':416,'msg':response_code[416]})
        
class ActivateAccount(GenericAPIView):
    serializer_class = LoginSerializer

    def get(self, request, surl):
        try:
            token_obj = ShortURL.objects.get(surl=surl)
        except Exception:
            return Response({'code':409,'msg':response_code[409]})
        token     = token_obj.lurl
        try:
            decode    = jwt.decode(token, 'secret')
        except jwt.DecodeError:
            return Response({'code':304,'msg':response_code[304]})
        username  = decode['username']
        try:
            validate_user_does_not_exists(username)
        except UsernameDoesNotExistsError as e:
            return Response({'code':e.code, 'msg':e.msg})
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
        email = request.data.get('email')
        try:
            validate_email(email)
        except ValidationError:
            return Response({'code':404,'msg':response_code[404]})
        user = User.objects.filter(email=email)
        try:
            username = user.values()[0]['username'] 
        except IndexError:
            return Response({'code':303,'msg':response_code[303]})
        try:            
            send_forgot_password_mail(request, username)
            return Response({'code':200,'msg':response_code[200]})
        except SMTPException:
            return Response({'code':301,'msg':response_code[301]})

class ResetNewPassword(GenericAPIView):
    serializer_class = ResetPasswordSerializer

    def post(self, request, *args, **kwargs):
        surl= kwargs.get('surl')
        try:
            token_obj = ShortURL.objects.get(surl=surl)
        except Exception:
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

 