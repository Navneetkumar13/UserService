from django.db import models

class FollowMap(models.Model):
    followee = models.CharField(max_length=256)
    following = models.CharField(max_length=256)
