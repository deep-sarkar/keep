from .exceptions import (PasswordDidntMatched,
                        PasswordPatternMatchError, 
                        UsernameAlreadyExistsError,
                        EmailAlreadyExistsError,
                        UsernameDoesNotExistsError,
                        )
from status import response_code
from django.contrib.auth import get_user_model


User = get_user_model()


#Regex
import re

def validate_password_match(password1,password2):
    if password1 != password2:
        raise PasswordDidntMatched(code=403,msg=response_code[403])

def validate_password_pattern_match(password):
    if not re.search('^[a-zA-Z0-9]{8,}$',password):
        raise PasswordPatternMatchError(code=406,msg=response_code[406])

def validate_duplicat_username_existance(username):
    if User.objects.filter(username=username).exists():
        raise UsernameAlreadyExistsError(code=401,msg=response_code[401])

def validate_duplicate_email_existance(email):
    if User.objects.filter(email=email).exists():
        raise EmailAlreadyExistsError(code=408,msg=response_code[408])

def validate_user_does_not_exists(username):
    if not User.objects.filter(username=username).exists():
        raise UsernameDoesNotExistsError(code=409,msg=response_code[409])

def validate_email_does_not_exists(username):
    if not User.objects.filter(username=username).exists():
        raise UsernameDoesNotExistsError(code=409,msg=response_code[409])
        