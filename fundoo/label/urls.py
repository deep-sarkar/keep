from django.urls import path
from label.views import GetLabel, CreateLabel

urlpatterns = [
    path('create/', CreateLabel.as_view()),
    path('get/', GetLabel.as_view()),
]
