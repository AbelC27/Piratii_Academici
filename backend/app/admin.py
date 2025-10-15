from django.contrib import admin
from .models import Problem, Submission
from django.contrib.auth.models import User

# Register your models here.

def register(model_class):
    admin.site.register(model_class)

register(Problem)
register(Submission)
# User is already registered by Django's auth system
# If you want to customize it, use: admin.site.unregister(User) then re-register