from django.urls import path
from .views import(Registration, 
                    LoginAPIView, 
                    Logout, 
                    ResetPasswordView, 
                    ActivateAccount, 
                    ForgotPasswordView,
                    CheckUserExistance,
                    ResetNewPassword
                    ) 
from rest_framework_jwt.views import refresh_jwt_token


urlpatterns = [
    path('register/', Registration.as_view(), name='registration'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('logout/', Logout.as_view(), name='logout'),
    path('change_password/',ResetPasswordView.as_view(), name='change_password'),
    path('activate/<surl>/', ActivateAccount.as_view(), name='activate'),
    path('forgot_password/',ForgotPasswordView.as_view(), name='forgot_password'),
    path('check_user/<surl>/',CheckUserExistance.as_view(), name='checkUserExistance'),
    path('reset_paassword/', ResetNewPassword.as_view(), name='reset_new_password'),
    path('token_refresh/', refresh_jwt_token)
]