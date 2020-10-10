from django.db import models
from django.contrib.auth.models import User
from label.models import Label
    
class Note(models.Model):
    user      = models.ForeignKey(User, on_delete=models.CASCADE)
    title     = models.CharField(max_length = 100, default='')
    note      = models.TextField(default='') 
    image     = models.ImageField(blank = True, null = True)
    reminder  = models.DateTimeField(auto_now = False,auto_now_add = False, null = True, blank = True)
    archive   = models.BooleanField(default=False)
    trash     = models.BooleanField(default=False)
    pin       = models.BooleanField(default=False)
    color     = models.CharField(max_length = 7, default = '#ffffff')
    labels    = models.ManyToManyField(Label, through='LabelMap', related_name='label')
    collaborators = models.ManyToManyField(User, through='UserMap', related_name='user')

    def __str__(self):
        return self.title


class LabelMap(models.Model):
    note  = models.ForeignKey(Note, on_delete = models.CASCADE)
    label = models.ForeignKey(Label, on_delete = models.DO_NOTHING)
    

    class Meta:
        unique_together = [['note','label']]

class UserMap(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    note = models.ForeignKey(Note, on_delete=models.DO_NOTHING)

    class Meta:
        unique_together = [['note','user']]