import datetime
from random import choice
from django.core.management.base import BaseCommand
from app.models import DailyChallenge, Problem

class Command(BaseCommand):
    help = 'Creates daily challenges for a specified number of past days'

    def add_arguments(self, parser):
        parser.add_argument(
            'days',
            type=int,
            help='The number of past days to create challenges for',
            default=7  # Default to 7 days if not specified
        )
    def handle(self, *args, **kwargs):
        days_to_create = kwargs['days']
        today = datetime.date.today()
        
        # Get all hard problems once to avoid re-querying in loop
        hard_problems = list(Problem.objects.filter(difficulty='hard'))
        
        if not hard_problems:
            # Fallback to any difficulty
            hard_problems = list(Problem.objects.all())
        
        if not hard_problems:
            self.stdout.write(
                self.style.ERROR('No problems available in the database to create challenges!')
            )
            return

        self.stdout.write(
            self.style.SUCCESS(f'--- Creating challenges for the past {days_to_create} days ---')
        )
        
        created_count = 0
        skipped_count = 0

        for i in range(1, days_to_create + 1):
            target_date = today - datetime.timedelta(days=i)
            
            # Check if challenge already exists for this date
            if DailyChallenge.objects.filter(date=target_date).exists():
                self.stdout.write(
                    self.style.WARNING(f'Challenge for {target_date} already exists, skipping.')
                )
                skipped_count += 1
                continue
            
            # Create daily challenge for the past date
            problem = choice(hard_problems)
            challenge = DailyChallenge.objects.create(
                date=target_date,
                problem=problem,
                bonus_points=10  # You can customize this
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created challenge for {target_date} (Problem ID: {problem.id})'
                )
            )
            created_count += 1
            
        self.stdout.write(
            self.style.SUCCESS(f'\n--- Summary ---')
        )
        self.stdout.write(f'✅ Created: {created_count} new challenges')
        self.stdout.write(f'⚠️ Skipped:  {skipped_count} existing challenges')