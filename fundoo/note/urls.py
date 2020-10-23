from django.urls import path
from note.views import ( 
                        CreateNote, 
                        GetNote, 
                        EditNote, 
                        TrashNote, 
                        ArchiveNote,
                        DeleteNote,
                        GetViewForAdmin
                        )

urlpatterns = [
    path('create/', CreateNote.as_view()),
    path('get/', GetNote.as_view()),
    path('get/all/', GetViewForAdmin.as_view()),
    path('edit/<int:id>/', EditNote.as_view()),
    path('trash/', TrashNote.as_view()),
    path('archive/', ArchiveNote.as_view()),
    path('delete/<int:id>/', DeleteNote.as_view())
]
