from django.contrib import admin
from .models import Note, Label, LabelMap

admin.site.register(Note)
admin.site.register(Label)
admin.site.register(LabelMap)
