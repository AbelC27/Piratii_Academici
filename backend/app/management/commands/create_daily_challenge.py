from django.core.management.base import BaseCommand
from app.models import DailyChallenge, Problem
from datetime import date
from random import choice


class Command(BaseCommand):
    help = 'Creates a daily challenge for today'

    def handle(self, *args, **kwargs):
        today = date.today()
        
        # Check if challenge already exists
        if DailyChallenge.objects.filter(date=today).exists():
            self.stdout.write(
                self.style.WARNING(f'Daily challenge for {today} already exists!')
            )
            return
        
        # Get a random hard problem
        hard_problems = Problem.objects.filter(difficulty='hard')
        
        if not hard_problems.exists():
            # Fallback to any difficulty
            hard_problems = Problem.objects.all()
        
        if not hard_problems.exists():
            self.stdout.write(
                self.style.ERROR('No problems available to create daily challenge!')
            )
            return
        
        # Create daily challenge
        problem = choice(hard_problems)
        challenge = DailyChallenge.objects.create(
            date=today,
            problem=problem,
            bonus_points=10
        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created daily challenge for {today}:\n'
                f'Problem: {problem.question}\n'
                f'Bonus Points: {challenge.bonus_points}'
            )
        )
