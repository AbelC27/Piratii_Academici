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


# --- PIRATE MAP JOURNEY FEATURE ---
class MapCheckpoint(models.Model):
    """
    Represents a checkpoint/island on the pirate map journey.
    Users unlock checkpoints sequentially by solving problems.
    """
    DIFFICULTY_LEVELS = [
        (1, 'Beginner Bay'),
        (2, 'Sailor\'s Strait'),
        (3, 'Corsair Cove'),
        (4, 'Captain\'s Channel'),
        (5, 'Legend\'s Lagoon'),
    ]
    
    checkpoint_number = models.IntegerField(unique=True, db_index=True)  # Sequential order (1, 2, 3...)
    name = models.CharField(max_length=100)  # e.g., "Treasure Island", "Skull Cove"
    description = models.TextField(blank=True)  # Lore/story for the checkpoint
    emoji = models.CharField(max_length=10, default='🏝️')  # Visual representation
    difficulty_level = models.IntegerField(choices=DIFFICULTY_LEVELS, default=1)
    
    # Position on the map (for visual display)
    position_x = models.IntegerField(default=0)  # X coordinate percentage (0-100)
    position_y = models.IntegerField(default=0)  # Y coordinate percentage (0-100)
    
    # Requirements
    problems_to_unlock = models.IntegerField(default=3)  # Number of problems to solve to unlock next
    points_reward = models.IntegerField(default=10)  # Points awarded when completing this checkpoint
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['checkpoint_number']
    
    def __str__(self):
        return f"#{self.checkpoint_number}: {self.name} ({self.emoji})"
    
    @property
    def next_checkpoint(self):
        """Get the next checkpoint in sequence"""
        try:
            return MapCheckpoint.objects.get(checkpoint_number=self.checkpoint_number + 1)
        except MapCheckpoint.DoesNotExist:
            return None
    
    @property
    def previous_checkpoint(self):
        """Get the previous checkpoint in sequence"""
        if self.checkpoint_number <= 1:
            return None
        try:
            return MapCheckpoint.objects.get(checkpoint_number=self.checkpoint_number - 1)
        except MapCheckpoint.DoesNotExist:
            return None


class UserProgress(models.Model):
    """
    Tracks each user's progress through the pirate map journey.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='map_progress')
    current_checkpoint = models.ForeignKey(
        MapCheckpoint, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='current_users'
    )
    
    # Tracking
    problems_solved_at_current = models.IntegerField(default=0)  # Progress at current checkpoint
    total_checkpoints_completed = models.IntegerField(default=0)
    total_map_problems_solved = models.IntegerField(default=0)
    
    # Timestamps
    journey_started_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User Map Progress'
        verbose_name_plural = 'User Map Progresses'
    
    def __str__(self):
        checkpoint_name = self.current_checkpoint.name if self.current_checkpoint else "Not Started"
        return f"{self.user.username} - At: {checkpoint_name}"
    
    def can_advance(self):
        """Check if user can advance to next checkpoint"""
        if not self.current_checkpoint:
            return False
        return self.problems_solved_at_current >= self.current_checkpoint.problems_to_unlock
    
    def advance_to_next_checkpoint(self):
        """Move user to the next checkpoint if requirements are met"""
        if not self.can_advance():
            return False
        
        next_checkpoint = self.current_checkpoint.next_checkpoint
        if next_checkpoint:
            # Award points for completing checkpoint
            self.user.userprofile.points += self.current_checkpoint.points_reward
            self.user.userprofile.save()
            
            # Move to next checkpoint
            self.current_checkpoint = next_checkpoint
            self.problems_solved_at_current = 0
            self.total_checkpoints_completed += 1
            self.save()
            return True
        return False  # No more checkpoints
    
    def record_problem_solved(self):
        """Record that user solved a problem at current checkpoint"""
        self.problems_solved_at_current += 1
        self.total_map_problems_solved += 1
        self.save()
        
        # Check if can auto-advance
        if self.can_advance():
            return self.advance_to_next_checkpoint()
        return False


@receiver(post_save, sender=User)
def create_user_progress(sender, instance, created, **kwargs):
    """Create UserProgress when a new User is created."""
    if created:
        # Get the first checkpoint or create user progress without checkpoint
        first_checkpoint = MapCheckpoint.objects.filter(checkpoint_number=1).first()
        UserProgress.objects.create(user=instance, current_checkpoint=first_checkpoint)