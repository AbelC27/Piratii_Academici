"""
Script to populate the database with math problems
Run with: python populate_problems.py
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PBMate.settings')
django.setup()

from app.models import Problem

# Clear existing problems (optional)
# Problem.objects.all().delete()
print("Current problems count:", Problem.objects.count())

# --- Arithmetic Problems (Existing) ---
arithmetic_easy = [
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
]
arithmetic_medium = [
    ("12 + 18", "30"),
    ("25 - 13", "12"),
    ("15 × 6", "90"),
    ("48 ÷ 8", "6"),
    ("23 + 37", "60"),
    ("45 - 28", "17"),
    ("12 × 9", "108"),
    ("72 ÷ 9", "8"),
]
arithmetic_hard = [
    ("123 + 456", "579"),
    ("789 - 234", "555"),
    ("25 × 24", "600"),
    ("144 ÷ 12", "12"),
    ("345 + 678", "1023"),
    ("987 - 543", "444"),
    ("32 × 17", "544"),
    ("225 ÷ 15", "15"),
]

# --- NEW: Algebra Problems ---
algebra_easy = [
    ("Solve for x: x + 5 = 10", "5"),
    ("Solve for y: y - 3 = 7", "10"),
    ("Solve for a: 2a = 12", "6"),
    ("Solve for b: b / 4 = 3", "12"),
]
algebra_medium = [
    ("Solve for x: 2x + 3 = 11", "4"),
    ("Solve for y: 3y - 5 = 10", "5"),
    ("Solve for a: a / 2 + 1 = 5", "8"),
    ("Solve for b: 4(b - 1) = 12", "4"),
]
algebra_hard = [
    ("Solve for x: 5x - 7 = 3x + 5", "6"),
    ("Solve for y: 2(y + 3) = 18", "6"),
    ("Solve for a: a / 3 + 2 = a / 4 + 3", "12"),
    ("Solve for b: (b + 1) / 5 = 2", "9"),
]

# --- NEW: Fractions Problems ---
fractions_easy = [
    ("1/2 + 1/4", "3/4"),
    ("3/5 - 1/5", "2/5"),
    ("1/3 × 2/3", "2/9"),
    ("What is half of 10?", "5"), # Word problem style
]
fractions_medium = [
    ("1/2 + 1/3", "5/6"),
    ("3/4 - 1/8", "5/8"),
    ("2/5 × 5/6", "1/3"),
    ("3/4 ÷ 1/2", "3/2"), # or 1.5 - decide on answer format
]
fractions_hard = [
    ("5/6 + 3/8", "29/24"),
    ("7/10 - 2/5", "3/10"),
    ("3/7 × 14/15", "2/5"),
    ("5/9 ÷ 10/3", "1/6"),
]

# Function to add problems, avoiding duplicates
def add_problem_batch(problems_list, difficulty, category):
    added_count = 0
    for question, answer in problems_list:
        if not Problem.objects.filter(question__iexact=question).exists():
            Problem.objects.create(
                question=question,
                answer=answer,
                difficulty=difficulty,
                category=category
            )
            added_count += 1
    return added_count

# --- Create problems by category and difficulty ---
created_total = 0

print("\nAdding Arithmetic problems...")
created_total += add_problem_batch(arithmetic_easy, 'easy', 'arithmetic')
created_total += add_problem_batch(arithmetic_medium, 'medium', 'arithmetic')
created_total += add_problem_batch(arithmetic_hard, 'hard', 'arithmetic')

print("Adding Algebra problems...")
created_total += add_problem_batch(algebra_easy, 'easy', 'algebra')
created_total += add_problem_batch(algebra_medium, 'medium', 'algebra')
created_total += add_problem_batch(algebra_hard, 'hard', 'algebra')

print("Adding Fractions problems...")
created_total += add_problem_batch(fractions_easy, 'easy', 'fractions')
created_total += add_problem_batch(fractions_medium, 'medium', 'fractions')
created_total += add_problem_batch(fractions_hard, 'hard', 'fractions')

# --- Updated Summary ---
print(f"\n✅ Successfully created {created_total} new problems!")
print(f"📊 Total problems in database: {Problem.objects.count()}")

# Print counts per category
print("\n--- Counts per Category ---")
for category_code, category_name in Problem.CATEGORY_CHOICES:
    count = Problem.objects.filter(category=category_code).count()
    print(f"   - {category_name}: {count}")

# Print counts per difficulty
print("\n--- Counts per Difficulty ---")
print(f"   - Easy: {Problem.objects.filter(difficulty='easy').count()}")
print(f"   - Medium: {Problem.objects.filter(difficulty='medium').count()}")
print(f"   - Hard: {Problem.objects.filter(difficulty='hard').count()}")