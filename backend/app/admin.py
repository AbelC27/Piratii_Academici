from django.contrib import admin
from .models import Problem, User

# Register your models here.

def register(model_class):
    admin.site.register(model_class)

register(Problem)
register(User)