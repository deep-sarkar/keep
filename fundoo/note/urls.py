from django.urls import path
from note.views import CreateNote, GetNote, EditNote

urlpatterns = [
    path('create/', CreateNote.as_view()),
    path('get/', GetNote.as_view()),
    path('edit/<int:id>/', EditNote.as_view()),
]