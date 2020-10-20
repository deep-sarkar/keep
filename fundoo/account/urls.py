from django.urls import path
from .views import(Registration, 
                    LoginAPIView, 
                    Logout, 
                    ChangePasswordView, 
                    ActivateAccount, 
                    ForgotPasswordView,
                    ResetNewPassword,
                    RefreshToken
                    ) 


urlpatterns = [
    path('register/', Registration.as_view(), name='registration'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('logout/', Logout.as_view(), name='logout'),
    path('change_password/',ChangePasswordView.as_view(), name='change_password'),
    path('activate/<stoken>/', ActivateAccount.as_view(), name='activate'),
    path('forgot_password/',ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset_password/<str:stoken>/', ResetNewPassword.as_view(), name='reset_new_password'),
    path('refresh_token/', RefreshToken.as_view())
]