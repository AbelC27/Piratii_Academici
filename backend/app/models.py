from django.db import models
from django.utils import timezone
from datetime import date

# Create your models here.
class Problem(models.Model):
    id = models.AutoField(primary_key=True)
    question = models.CharField(max_length=255)
    answer = models.CharField(max_length=255)
    difficulty = models.CharField(max_length=50)
    solved_by = models.ManyToManyField('auth.User', related_name='solved_problems', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.question} = {self.answer} (Difficulty: {self.difficulty})"
    
class Submission(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    submitted_answer = models.CharField(max_length=255)
    was_correct = models.BooleanField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Submission by {self.user.username} for Problem {self.problem.id}: {'✓' if self.was_correct else '✗'}"

class DailyChallenge(models.Model):
    """
    Daily Challenge - a special problem for each day
    """
    date = models.DateField(unique=True, default=date.today)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    bonus_points = models.IntegerField(default=10)  # Extra points for completing daily challenge
    completed_by = models.ManyToManyField('auth.User', related_name='completed_challenges', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f"Daily Challenge for {self.date}: {self.problem.question}"
    
    @classmethod
    def get_today_challenge(cls):
        """Get or create today's challenge"""
        today = date.today()
        try:
            return cls.objects.get(date=today)
        except cls.DoesNotExist:
            from random import choice
            hard_problems = Problem.objects.filter(difficulty='hard')
            if hard_problems.exists():
                problem = choice(hard_problems)
                return cls.objects.create(date=today, problem=problem)
            return None
    
    def is_completed_by(self, user):
        """Check if user has completed this challenge"""
        return user in self.completed_by.all()