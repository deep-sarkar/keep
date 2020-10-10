from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

#import from django
from django.contrib.auth import get_user_model, login, logout, authenticate
from django.core.validators import validate_email
from django.template.loader import render_to_string
from django.shortcuts import redirect, HttpResponse, render


#Short url
from django_short_url.views import get_surl
from django_short_url.models import ShortURL

#mailing
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from fundoo.settings import EMAIL_HOST_USER


#import from serializers
from .serializers import (RegistrationSerializer, 
                          LoginSerializer, 
                          ResetPasswordSerializer, 
                          ForgotPasswordSerializer)

#token
from account.services.token_service import generate_token

#errors
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from .exceptions import (PasswordDidntMatched, 
                        PasswordPatternMatchError,
                        UsernameAlreadyExistsError,
                        EmailAlreadyExistsError,
                        UsernameDoesNotExistsError,
                        EmailDoesNotExistsError,
                        UserCreationError
                        )
from smtplib import SMTPException

#regular expression
import re

#validator
from .validation_function import (validate_password_match,
                       validate_password_pattern_match,
                       validate_duplicat_username_existance,
                       validate_duplicate_email_existance,
                       validate_user_does_not_exists,
                       validate_email_does_not_exists,
                      )   

from account.validate import validate_registration

from account.services.email_services import send_account_activation_mail
from account.services.repository import create_user

from rest_framework_jwt.settings import api_settings
import jwt

#User model
User = get_user_model()

#redis object
from . import redis
from django.core.cache import cache

#Static data
from util import static_data
from util.status import response_code

jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER

#Home

class Registration(GenericAPIView):
    serializer_class = RegistrationSerializer
    

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return Response({'code':410,'msg':response_code[410]})
        valid = validate_registration(request)
        if valid != None:
            return Response(valid)
        try:
            create_user(request)
            send_account_activation_mail(request)
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
        try:
            validate_user_does_not_exists(username)
            validate_password_pattern_match(password)
        except UsernameDoesNotExistsError as e:
            return Response({'code':e.code,'msg':e.msg})
        except PasswordPatternMatchError as e :
            return Response({'code':e.code,'msg':e.msg})
        user_obj = authenticate(request, username=username, password=password)
        if user_obj is not None:
            if user_obj.is_active:
                login(request,user_obj)
                payload = jwt_payload_handler(user_obj)
                token = jwt_encode_handler(payload)
                redis.set_attribute(username,token)
                return Response({'code':200,'msg':response_code[200],'token':token})
            return Response({'code':411,'msg':response_code[411]})
        return Response({'code':412,'msg':response_code[412]})

class Logout(GenericAPIView):
    serializer_class = LoginSerializer

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({'code':413, 'msg':response_code[413]})
        username = request.user.username
        user_id  = request.user.id
        cache_key = str(username)+str(user_id)
        cache.delete(cache_key)
        redis.delete_attribute(username)
        logout(request)
        return Response({'code':200,'msg':response_code[200]})

class ResetPasswordView(GenericAPIView):
    serializer_class = ResetPasswordSerializer

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({'code':413, 'msg':response_code[413]})
        username         = self.request.user.username
        password         = request.data.get('password')
        confirm_password = request.data.get('confirm_password')
        try:
            validate_password_pattern_match(password)
            validate_password_match(password,confirm_password)
            validate_user_does_not_exists(username)
        except PasswordDidntMatched as e:
            return Response({"code":e.code,"msg":e.msg})
        except PasswordPatternMatchError as e:
            return Response({"code":e.code,"msg":e.msg})
        except UsernameDoesNotExistsError as e:
            return Response({'code':e.code,'msg':e.msg})
        user = User.objects.get(username=username)
        user.set_password(password)
        user.save()
        return Response({'code':200, 'msg':response_code[200]})
        
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
        payload = {
                'username': username,
                }
        token = generate_token(payload)
        current_site = get_current_site(request)
        domain_name = current_site.domain
        surl = get_surl(str(token))
        final_url = surl.split("/")
        mail_subject = static_data.PASSWORD_RESET_MESSAGE
        msg = render_to_string(
            'account/forgot_password.html',
            {
                'username': username, 
                'domain': domain_name,
                'surl': final_url[2],
                })
        try:            
            send_mail(mail_subject, msg, EMAIL_HOST_USER,
                    [email], fail_silently=False)
            return Response({'code':200,'msg':response_code[200]})
        except SMTPException:
            return Response({'code':301,'msg':response_code[301]})

class CheckUserExistance(GenericAPIView):
    serializer_class = LoginSerializer

    def get(self, request, surl):
        try:
            token_obj = ShortURL.objects.get(surl=surl)
        except Exception:
            return Response({'code':409,'msg':response_code[409]})
        token = token_obj.lurl
        try:
            decode = jwt.decode(token,'SECRET_KEY')
        except jwt.DecodeError:
            return Response({'code':304,'msg':response_code[304]})
        username = decode['username']
        user = User.objects.get(username=username)
        if user is not None:
            return Response({'code':203,'msg':response_code[203]})
        else:
            return Response({'code':306,'msg':response_code[306]})

   
class ResetNewPassword(GenericAPIView):
    serializer_class = ResetPasswordSerializer

    def post(self, request):
        surl= request.data.get('surl')
        try:
            token_obj = ShortURL.objects.get(surl=surl)
        except Exception:
            return Response({'code':409,'msg':response_code[409]})
        token = token_obj.lurl
        try:
            decode = jwt.decode(token,'SECRET_KEY')
        except jwt.DecodeError:
            return Response({'code':304,'msg':response_code[304]})
        username = decode['username']
        password         = request.data.get('password')
        confirm_password = request.data.get('confirm_password')
        try:
            validate_password_match(password, confirm_password)
            validate_password_pattern_match(password)
        except PasswordDidntMatched as e:
            return Response({"code":e.code,"msg":e.msg})
        except PasswordPatternMatchError as e:
            return Response({"code":e.code,"msg":e.msg})
        user = User.objects.get(username__exact=username)
        if user is not None:
            user.set_password(password)
            user.save()
            return Response({'code':200,'msg':response_code[200]})
        return Response({'code':409,'msg':response_code[409]})

 