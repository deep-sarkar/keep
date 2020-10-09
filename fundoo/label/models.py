from django.db import models
from django.contrib.auth.models import User

class Label(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length = 20, blank=True, null=True)

    class Meta:
        unique_together = [['name','user']]

    def __str__(self):
        return self.name