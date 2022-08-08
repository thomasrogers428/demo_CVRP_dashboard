# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class User(AbstractUser):
    subscribe_newsletters = models.BooleanField(default=True)
    old_id = models.IntegerField(null=True, blank=True)
    old_source = models.CharField(max_length=25, null=True, blank=True)
