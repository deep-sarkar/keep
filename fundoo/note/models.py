from django.db import models
from django.contrib.auth.models import User

class Note(models.Model):
    user      = models.ForeignKey(User, on_delete=models.CASCADE)
    title     = models.CharField(max_length = 100, blank=False, null=False)
    note      = models.TextField(blank = False, null = False) 
    image     = models.ImageField(blank = True, null = True)
    reminder  = models.DateTimeField(auto_now = False,auto_now_add = False, null = True, blank = True)
    archive   = models.BooleanField(default=False)
    trash     = models.BooleanField(default=False)
    pin       = models.BooleanField(default=False)
    color     = models.CharField(max_length = 7, default = '#ffffff')

    def __str__(self):
        return self.title
