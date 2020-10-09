from django.urls import path
from label.views import GetLabel, CreateLabel, EditLabel, DeleteLabel

urlpatterns = [
    path('create/', CreateLabel.as_view()),
    path('get/', GetLabel.as_view()),
    path('edit/<int:id>/', EditLabel.as_view()),
    path('delete/<int:id>/', DeleteLabel.as_view()),
]
