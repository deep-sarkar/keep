from django.urls import path
from note.views import CreateNote, GetNote, EditNote, TrashNote, CreateLabel

urlpatterns = [
    path('create/', CreateNote.as_view()),
    path('get/', GetNote.as_view()),
    path('edit/<int:id>/', EditNote.as_view()),
    path('trash/', TrashNote.as_view()),
    path('label/', CreateLabel.as_view())
]
