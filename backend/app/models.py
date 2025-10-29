from django.db import models
from django.utils import timezone
from datetime import date
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
class Problem(models.Model):
    # --- ADD THESE CATEGORY CHOICES ---
    CATEGORY_CHOICES = [
        ('arithmetic', 'Arithmetic'),
        ('algebra', 'Algebra'),
        ('fractions', 'Fractions'),
    ]
    # ------------------------------------

    id = models.AutoField(primary_key=True)
    question = models.CharField(max_length=255)
    answer = models.CharField(max_length=255)
    difficulty = models.CharField(max_length=50) # Should be 'easy', 'medium', or 'hard'
    
    # --- ADD THE CATEGORY FIELD ---
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default='arithmetic'
    )
    # ------------------------------

    solved_by = models.ManyToManyField('auth.User', related_name='solved_problems', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        # --- UPDATE STR METHOD ---
        return f"[{self.get_category_display()}] {self.question} = {self.answer} ({self.difficulty})"

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
            # Ensure we only pick from 'hard' problems as per the original management command
            hard_problems = Problem.objects.filter(difficulty='hard')
            if not hard_problems.exists():
                # Fallback to any problem if no hard ones exist
                hard_problems = Problem.objects.all()

            if hard_problems.exists():
                problem = choice(hard_problems)
                return cls.objects.create(date=today, problem=problem)
            return None # No problems in DB at all

    def is_completed_by(self, user):
        """Check if user has completed this challenge"""
        return user in self.completed_by.all()


# --- NEW FEATURE: User Profile & Points System ---

class UserProfile(models.Model):
    """
    Stores user points and other profile-specific info.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)

    # --- ADDED FOR STREAKS ---
    current_streak = models.IntegerField(default=0)
    last_daily_challenge_date = models.DateField(null=True, blank=True)
    # -------------------------

    # --- ADDED FOR AVATAR ---
    avatar = models.CharField(max_length=5, default='👤') # Allow a bit more length for complex emojis
    # ------------------------

    def __str__(self):
        return f"{self.user.username}'s Profile ({self.points} points)"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a UserProfile whenever a new User is created."""
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save the UserProfile whenever the User is saved."""
    try:
        instance.userprofile.save()
    except UserProfile.DoesNotExist:
        # This handles users created before the UserProfile model existed
        UserProfile.objects.create(user=instance)


# --- ADD THIS NEW MODEL FOR FEATURE 4 ---
class SpeedRunAttempt(models.Model):
    """
    Stores the result of a single speed run game.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='speed_run_attempts')
    score = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-score', '-created_at']

    def __str__(self):
        return f"{self.user.username}'s attempt: {self.score} points ({self.created_at.date()})"