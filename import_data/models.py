from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.db import models

class Question(models.Model):
    title = models.CharField(max_length=255)
    user = models.ForeignKey('User', null=True)
    tags = models.ManyToManyField('Tag')

class Tag(models.Model):
    title = models.CharField(max_length=255)

class User(models.Model):
    title = models.CharField(max_length=255)
