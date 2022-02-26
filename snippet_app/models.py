from django.contrib.auth import get_user_model
from django.db import models

USER_MODEL = get_user_model()


class Tag(models.Model):
    title = models.CharField(max_length=250, unique=True)

    def __str__(self):
        return f'{self.title}'


class Snippet(models.Model):
    title = models.CharField(max_length=250)
    content = models.TextField()
    created_on = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(USER_MODEL, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.title}'
