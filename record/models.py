from django.conf import settings
from django.core.validators import MinLengthValidator
from django.db import models


class Record(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-id']


class Word(models.Model):
    record = models.ForeignKey(Record, on_delete=models.CASCADE)
    word = models.TextField()
    count = models.IntegerField()
