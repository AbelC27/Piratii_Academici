"""
Django management command to populate the pirate map with checkpoints.
Run with: python manage.py populate_pirate_map
"""
from django.core.management.base import BaseCommand
from app.models import MapCheckpoint


class Command(BaseCommand):
    help = 'Populate the pirate map with initial checkpoints'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🏴‍☠️ Setting up the Pirate Map Journey...'))
        
        # Clear existing checkpoints if rerunning
        MapCheckpoint.objects.all().delete()
        
        # Define the pirate journey checkpoints
        checkpoints = [
            {
                'checkpoint_number': 1,
                'name': 'Rookie Bay',
                'description': 'Where every pirate\'s journey begins. Master the basics of mathematics here!',
                'emoji': '⛵',
                'difficulty_level': 1,
                'position_x': 10,
                'position_y': 80,
                'problems_to_unlock': 3,
                'points_reward': 10,
            },
            {
                'checkpoint_number': 2,
                'name': 'Calculation Cove',
                'description': 'A peaceful harbor where pirates sharpen their calculation skills.',
                'emoji': '🏝️',
                'difficulty_level': 1,
                'position_x': 25,
                'position_y': 65,
                'problems_to_unlock': 4,
                'points_reward': 15,
            },
            {
                'checkpoint_number': 3,
                'name': 'Fraction Fjord',
                'description': 'Navigate the treacherous waters of fractions and decimals.',
                'emoji': '⚓',
                'difficulty_level': 2,
                'position_x': 40,
                'position_y': 50,
                'problems_to_unlock': 5,
                'points_reward': 20,
            },
            {
                'checkpoint_number': 4,
                'name': 'Algebra Archipelago',
                'description': 'A chain of islands where algebra mysteries await!',
                'emoji': '🗺️',
                'difficulty_level': 3,
                'position_x': 55,
                'position_y': 35,
                'problems_to_unlock': 5,
                'points_reward': 25,
            },
            {
                'checkpoint_number': 5,
                'name': 'Equation Estuary',
                'description': 'Where rivers of equations meet the sea of solutions.',
                'emoji': '🌊',
                'difficulty_level': 3,
                'position_x': 65,
                'position_y': 55,
                'problems_to_unlock': 6,
                'points_reward': 30,
            },
            {
                'checkpoint_number': 6,
                'name': 'Geometry Gulf',
                'description': 'Discover the shapes and angles hidden in these waters.',
                'emoji': '📐',
                'difficulty_level': 4,
                'position_x': 75,
                'position_y': 40,
                'problems_to_unlock': 6,
                'points_reward': 35,
            },
            {
                'checkpoint_number': 7,
                'name': 'Problem Port',
                'description': 'A bustling port where complex problems dock.',
                'emoji': '⚔️',
                'difficulty_level': 4,
                'position_x': 80,
                'position_y': 65,
                'problems_to_unlock': 7,
                'points_reward': 40,
            },
            {
                'checkpoint_number': 8,
                'name': 'Treasure Island',
                'description': 'The legendary island where only the bravest pirates dare to land!',
                'emoji': '💎',
                'difficulty_level': 5,
                'position_x': 90,
                'position_y': 50,
                'problems_to_unlock': 8,
                'points_reward': 50,
            },
            {
                'checkpoint_number': 9,
                'name': 'Captain\'s Challenge',
                'description': 'Prove yourself worthy of becoming a true Math Captain!',
                'emoji': '👑',
                'difficulty_level': 5,
                'position_x': 85,
                'position_y': 20,
                'problems_to_unlock': 10,
                'points_reward': 75,
            },
            {
                'checkpoint_number': 10,
                'name': 'Legend\'s Lagoon',
                'description': 'The final destination. Only legendary math pirates reach this sacred place!',
                'emoji': '🏆',
                'difficulty_level': 5,
                'position_x': 95,
                'position_y': 30,
                'problems_to_unlock': 12,
                'points_reward': 100,
            },
        ]
        
        created_count = 0
        for checkpoint_data in checkpoints:
            checkpoint = MapCheckpoint.objects.create(**checkpoint_data)
            created_count += 1
            self.stdout.write(
                self.style.SUCCESS(
                    f'  ✓ Created checkpoint #{checkpoint.checkpoint_number}: '
                    f'{checkpoint.emoji} {checkpoint.name}'
                )
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎉 Successfully created {created_count} pirate map checkpoints!'
            )
        )
        self.stdout.write(
            self.style.WARNING(
                '\n⚠️  Note: Existing users will need to reload the page to see the map.'
            )
        )
