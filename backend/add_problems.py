#!/usr/bin/env python3
"""
Script to populate the database with sample math problems
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PBMate.settings')
django.setup()

from app.models import Problem

# Sample problems
problems = [
    {"question": "5 + 3", "answer": "8", "difficulty": "Easy"},
    {"question": "12 - 7", "answer": "5", "difficulty": "Easy"},
    {"question": "4 * 6", "answer": "24", "difficulty": "Easy"},
    {"question": "15 + 8 - 3", "answer": "20", "difficulty": "Medium"},
    {"question": "7 * 3 + 5", "answer": "26", "difficulty": "Medium"},
    {"question": "(8 + 2) * 3", "answer": "30", "difficulty": "Medium"},
    {"question": "25 - 15 + 10", "answer": "20", "difficulty": "Medium"},
    {"question": "6 * (5 - 2)", "answer": "18", "difficulty": "Medium"},
    {"question": "(12 + 8) * (5 - 3)", "answer": "40", "difficulty": "Hard"},
    {"question": "100 - 25 * 3 + 15", "answer": "40", "difficulty": "Hard"},
    {"question": "(15 - 7) * (6 + 4)", "answer": "80", "difficulty": "Hard"},
    {"question": "50 + 30 * 2 - 20", "answer": "90", "difficulty": "Hard"},
]

# Check what fields actually exist in Problem model
print(f"Problem model fields: {[f.name for f in Problem._meta.get_fields()]}")

print("=" * 60)
print("Adding Sample Math Problems")
print("=" * 60)

added = 0
skipped = 0

for prob_data in problems:
    # Check if problem already exists
    if Problem.objects.filter(question=prob_data["question"]).exists():
        print(f"⚠️  Skipped (exists): {prob_data['question']}")
        skipped += 1
        continue
    
    problem = Problem.objects.create(**prob_data)
    print(f"✅ Added: {problem.question} = {problem.answer} ({problem.difficulty})")
    added += 1

print("\n" + "=" * 60)
print(f"✅ Complete!")
print(f"   • Added: {added} problem(s)")
print(f"   • Skipped: {skipped} problem(s)")
print(f"   • Total in DB: {Problem.objects.count()} problem(s)")
print("=" * 60)
print("\n💡 Visit http://127.0.0.1:8000/problems/ to see them!\n")
