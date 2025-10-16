"""
Script to populate the database with math problems
Run with: python manage.py shell < populate_problems.py
Or: python populate_problems.py
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PBMate.settings')
django.setup()

from app.models import Problem

# Clear existing problems (optional)
print("Current problems count:", Problem.objects.count())

# Easy problems
easy_problems = [
    ("2 + 3", "5"),
    ("5 + 7", "12"),
    ("10 - 4", "6"),
    ("8 - 3", "5"),
    ("3 × 4", "12"),
    ("6 × 2", "12"),
    ("15 ÷ 3", "5"),
    ("20 ÷ 4", "5"),
    ("7 + 8", "15"),
    ("12 - 5", "7"),
    ("9 + 6", "15"),
    ("18 - 9", "9"),
    ("4 × 5", "20"),
    ("7 × 3", "21"),
    ("24 ÷ 6", "4"),
    ("30 ÷ 5", "6"),
]

# Medium problems
medium_problems = [
    ("12 + 18", "30"),
    ("25 - 13", "12"),
    ("15 × 6", "90"),
    ("48 ÷ 8", "6"),
    ("23 + 37", "60"),
    ("45 - 28", "17"),
    ("12 × 9", "108"),
    ("72 ÷ 9", "8"),
    ("34 + 56", "90"),
    ("88 - 39", "49"),
    ("11 × 7", "77"),
    ("63 ÷ 7", "9"),
    ("29 + 41", "70"),
    ("76 - 48", "28"),
    ("13 × 8", "104"),
    ("96 ÷ 12", "8"),
]

# Hard problems
hard_problems = [
    ("123 + 456", "579"),
    ("789 - 234", "555"),
    ("25 × 24", "600"),
    ("144 ÷ 12", "12"),
    ("345 + 678", "1023"),
    ("987 - 543", "444"),
    ("32 × 17", "544"),
    ("225 ÷ 15", "15"),
    ("567 + 890", "1457"),
    ("1000 - 678", "322"),
    ("45 × 23", "1035"),
    ("384 ÷ 16", "24"),
    ("234 + 567", "801"),
    ("876 - 432", "444"),
    ("28 × 35", "980"),
    ("576 ÷ 24", "24"),
    ("15 × 15", "225"),
    ("18 × 18", "324"),
    ("999 - 888", "111"),
    ("777 + 333", "1110"),
]

# Create problems
created = 0

for question, answer in easy_problems:
    if not Problem.objects.filter(question=question).exists():
        Problem.objects.create(
            question=question,
            answer=answer,
            difficulty='easy'
        )
        created += 1

for question, answer in medium_problems:
    if not Problem.objects.filter(question=question).exists():
        Problem.objects.create(
            question=question,
            answer=answer,
            difficulty='medium'
        )
        created += 1

for question, answer in hard_problems:
    if not Problem.objects.filter(question=question).exists():
        Problem.objects.create(
            question=question,
            answer=answer,
            difficulty='hard'
        )
        created += 1

print(f"\n✅ Successfully created {created} new problems!")
print(f"📊 Total problems in database: {Problem.objects.count()}")
print(f"   - Easy: {Problem.objects.filter(difficulty='easy').count()}")
print(f"   - Medium: {Problem.objects.filter(difficulty='medium').count()}")
print(f"   - Hard: {Problem.objects.filter(difficulty='hard').count()}")
