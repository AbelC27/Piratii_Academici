import os
from django.core.management.base import BaseCommand
from app.models import Problem  # Import your Problem model
from openai import OpenAI  # Import the OpenAI library

class Command(BaseCommand):
    help = 'Generates new math problems using the OpenAI API and adds them to the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=5,
            help='The number of problems to generate (default: 5)',
        )
        parser.add_argument(
            '--difficulty',
            type=str,
            default='medium',
            help='The difficulty of problems to generate (easy, medium, hard)',
        )
        # --- ADD ARGUMENT FOR CATEGORY ---
        parser.add_argument(
            '--category',
            type=str,
            default='arithmetic',
            help="The category of problems to generate (e.g., 'arithmetic', 'algebra', 'fractions')"
        )

    def handle(self, *args, **kwargs):
        count = kwargs['count']
        difficulty = kwargs['difficulty']
        # --- GET CATEGORY ---
        category = kwargs['category']

        # 1. Get the API key from environment variables
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            self.stdout.write(self.style.ERROR(
                'OPENAI_API_KEY environment variable not set. '
                'Please set it before running this command.'
            ))
            return
        
        # 2. Initialize the OpenAI client
        try:
            client = OpenAI(api_key=api_key)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to initialize OpenAI client: {e}'))
            return

        # 3. Define the prompt for the AI
        # --- MODIFIED PROMPT ---
        prompt = f"""
        Generate {count} new math problems with the following specifications:
        - The difficulty level must be: {difficulty}
        - The category must be: {category}
        - Provide the response as a list, with each problem on a new line.
        - Use the exact format: "Question text;Answer text;difficulty;category"
        - Do not include any other text, headers, or explanations.
        - Ensure the 'Answer' is just the final numerical answer or simple text (like '2/3').

        Example for 'arithmetic' (easy):
        5 * 8;40;easy;arithmetic
        
        Example for 'algebra' (medium):
        Solve for x: 2x + 4 = 10;3;medium;algebra

        Example for 'fractions' (hard):
        What is 3/4 * 8/9?;2/3;hard;fractions
        """

        self.stdout.write(self.style.SUCCESS(f'Sending prompt to OpenAI for {count} {difficulty} {category} problems...'))

        # 4. Call the API
        try:
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",  # A fast and cheap model
                messages=[
                    {"role": "system", "content": "You are a math problem generator."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            response_text = completion.choices[0].message.content
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'API call failed: {e}'))
            return

        # 5. Parse the response and save to database
        self.stdout.write(self.style.SUCCESS('Response received. Parsing and saving problems...'))
        
        created_count = 0
        skipped_count = 0
        
        # Split the response by new lines
        lines = response_text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue

            try:
                # Split by the semicolon
                parts = line.split(';')
                
                # --- UPDATE TO EXPECT 4 PARTS ---
                if len(parts) != 4:
                    self.stdout.write(self.style.WARNING(f'Skipping malformed line (expected 4 parts): {line}'))
                    continue
                    
                question, answer, prob_difficulty, prob_category = parts
                
                # Clean up and validate
                question = question.strip()
                answer = answer.strip()
                prob_difficulty = prob_difficulty.strip().lower()
                prob_category = prob_category.strip().lower()

                # Basic validation
                valid_categories = [c[0] for c in Problem.CATEGORY_CHOICES]
                if not all([question, answer, prob_difficulty in ['easy', 'medium', 'hard'], prob_category in valid_categories]):
                    self.stdout.write(self.style.WARNING(f'Skipping invalid data: {line}'))
                    continue
                    
                # Check if this exact question already exists
                if Problem.objects.filter(question__iexact=question).exists():
                    self.stdout.write(self.style.WARNING(f'Skipping duplicate problem: {question}'))
                    skipped_count += 1
                    continue
                    
                # --- CREATE PROBLEM WITH CATEGORY ---
                Problem.objects.create(
                    question=question,
                    answer=answer,
                    difficulty=prob_difficulty,
                    category=prob_category
                )
                created_count += 1
                self.stdout.write(f'  + Added: [{prob_category}] {question} ({prob_difficulty})')

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Failed to parse or save line "{line}": {e}'))

        self.stdout.write(self.style.SUCCESS(
            f'\nDone! Successfully added {created_count} new problems. Skipped {skipped_count} duplicates.'
        ))