from django.contrib.auth.models import User
from account.exceptions import UserCreationError
from util.status import response_code 


def create_user(request):
    try:
        first_name           = request.data.get('first_name')
        last_name            = request.data.get('last_name')
        username             = request.data.get('username')
        email                = request.data.get('email')
        password             = request.data.get('password')
        confirm              = request.data.get('confirm')
        user_obj = User.objects.create_user(first_name=first_name,
                                                last_name=last_name,
                                                username=username,
                                                email=email ,
                                                password=password
                                                )
        user_obj.is_active = False
        user_obj.save()
    except Exception:
        raise UserCreationError(code=309,msg=response_code[309])