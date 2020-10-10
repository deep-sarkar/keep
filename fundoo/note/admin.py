from django.contrib import admin
from .models import Note, LabelMap, UserMap

admin.site.register(Note)
admin.site.register(LabelMap)
admin.site.register(UserMap)
