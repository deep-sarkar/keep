from rest_framework.response import Response
from util.status import response_code

def custom_login_required(function):
    def wrap(request, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            # the decorator is passed and you can handle the request from the view
            return function(request, *args, **kwargs)
        else:
            return Response({"code":413,"msg":response_code[413]})
    return wrap


def admin_access_only(function):
    def wrap(request, *args, **kwargs):
        user = request.user
        if user.is_superuser:
            return function(request, *args, **kwargs)
        return Response({"code":419, "msg":response_code[419]})
    return wrap