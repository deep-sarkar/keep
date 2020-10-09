from django.urls import path
from note.views import ( 
                        CreateNote, 
                        GetNote, 
                        EditNote, 
                        TrashNote, 
                        CreateLabel,
                        ArchiveNote,
                        GetLabel
                        )

urlpatterns = [
    path('create/', CreateNote.as_view()),
    path('get/', GetNote.as_view()),
    path('edit/<int:id>/', EditNote.as_view()),
    path('trash/', TrashNote.as_view()),
    path('label/create/', CreateLabel.as_view()),
    path('archive/', ArchiveNote.as_view()),
    path('label/get/', GetLabel.as_view()),
]
