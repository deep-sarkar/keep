from django.db import models
from django.contrib.auth.models import User


class Label(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length = 20, blank=True, null=True)

    class Meta:
        unique_together = [['user','name']]

    def __str__(self):
        return self.name
    
class Note(models.Model):
    user      = models.ForeignKey(User, on_delete=models.CASCADE)
    title     = models.CharField(max_length = 100, blank=False, null=False)
    note      = models.TextField(blank = True, null = True) 
    image     = models.ImageField(blank = True, null = True)
    reminder  = models.DateTimeField(auto_now = False,auto_now_add = False, null = True, blank = True)
    archive   = models.BooleanField(default=False)
    trash     = models.BooleanField(default=False)
    pin       = models.BooleanField(default=False)
    color     = models.CharField(max_length = 7, default = '#ffffff')
    labels    = models.ManyToManyField(Label, through='LabelMap',related_name='label')

    def __str__(self):
        return self.title


class LabelMap(models.Model):
    note  = models.ForeignKey(Note, on_delete = models.CASCADE)
    label = models.ForeignKey(Label, on_delete = models.DO_NOTHING)

    def __str__(self):
        return super().__str__()

    class Meta:
        unique_together = [['note','label']]