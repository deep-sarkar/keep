from django.core.validators import validate_email
from account.exceptions import (PasswordDidntMatched, 
                        PasswordPatternMatchError,
                        UsernameAlreadyExistsError,
                        EmailAlreadyExistsError,
                        UsernameDoesNotExistsError,
                        EmailDoesNotExistsError
                        )
from django.core.exceptions import ValidationError
from util.status import response_code
from account.validation_function import *
                        

def validate_registration(request):
    first_name           = request.data.get('first_name')
    last_name            = request.data.get('last_name')
    username             = request.data.get('username')
    email                = request.data.get('email')
    password             = request.data.get('password')
    confirm     = request.data.get('confirm')
    try:
        validate_email(email)
        validate_password_match(password, confirm)
        validate_password_pattern_match(password)
        validate_duplicat_username_existance(username)
        validate_duplicate_email_existance(email)
    except ValidationError:
        return {'code':404,'msg':response_code[404]}        
    except PasswordDidntMatched as e:
        return {"code":e.code,"msg":e.msg}
    except PasswordPatternMatchError as e:
        return {"code":e.code,"msg":e.msg}
    except UsernameAlreadyExistsError as e:
        return {"code":e.code,"msg":e.msg}
    except EmailAlreadyExistsError as e:
        return {"code":e.code,"msg":e.msg}
    