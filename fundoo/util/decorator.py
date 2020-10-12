from django.shortcuts import redirect

def custom_login_required(function):
    def wrap(request, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            # the decorator is passed and you can handle the request from the view
            return function(request, *args, **kwargs)
        else:
            return redirect('login')
    return wrap