from django.contrib import admin
from .models import Problem, Submission, DailyChallenge
from django.contrib.auth.models import User

# Register your models here.

def register(model_class):
    admin.site.register(model_class)

register(Problem)
register(Submission)

# Register DailyChallenge with custom admin
@admin.register(DailyChallenge)
class DailyChallengeAdmin(admin.ModelAdmin):
    list_display = ('date', 'problem', 'bonus_points', 'get_completions_count')
    list_filter = ('date',)
    search_fields = ('problem__question',)
    date_hierarchy = 'date'
    
    def get_completions_count(self, obj):
        return obj.completed_by.count()
    get_completions_count.short_description = 'Completions'

# User is already registered by Django's auth system
# If you want to customize it, use: admin.site.unregister(User) then re-register