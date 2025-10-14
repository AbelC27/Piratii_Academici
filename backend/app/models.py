from django.db import models

# Create your models here.
class Problem(models.Model):
    id = models.AutoField(primary_key=True)
    question = models.CharField(max_length=255)
    expected = models.CharField(max_length=255)
    submitted = models.CharField(max_length=255)
    was_correct = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.question} = {self.submitted} ({'✓' if self.was_correct else '✗'})"




class User(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.username