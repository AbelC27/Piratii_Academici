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

    def handle(self, *args, **kwargs):
        count = kwargs['count']
        difficulty = kwargs['difficulty']

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
        # We ask for a specific format: "Question;Answer;Difficulty"
        prompt = f"""
        Generate {count} new math problems with the following specifications:
        - The difficulty level must be: {difficulty}
        - The problems should be arithmetic or simple word problems.
        - Provide the response as a list, with each problem on a new line.
        - Use the exact format: "Question text;Answer text;difficulty"
        - Do not include any other text, headers, or explanations.
        - Ensure the 'Answer' is just the final numerical answer.

        Example for 'easy':
        5 * 8;40;easy
        What is 15 + 22?;37;easy

        Example for 'medium':
        (10 + 5) * 3;45;medium
        A bus has 30 seats. 12 are empty. How many are full?;18;medium
        
        Example for 'hard':
        100 - (22 * 3);34;hard
        Sara buys 3 apples at $2 each and 2 bananas at $1 each. How much change does she get from $10?;2;hard
        """

        self.stdout.write(self.style.SUCCESS(f'Sending prompt to OpenAI for {count} {difficulty} problems...'))

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
                
                # Ensure we have exactly 3 parts
                if len(parts) != 3:
                    self.stdout.write(self.style.WARNING(f'Skipping malformed line: {line}'))
                    continue
                    
                question, answer, prob_difficulty = parts
                
                # Clean up and validate
                question = question.strip()
                answer = answer.strip()
                prob_difficulty = prob_difficulty.strip().lower()

                # Basic validation
                if not question or not answer or prob_difficulty not in ['easy', 'medium', 'hard']:
                    self.stdout.write(self.style.WARNING(f'Skipping invalid data: {line}'))
                    continue
                    
                # Check if this exact question already exists
                if Problem.objects.filter(question__iexact=question).exists():
                    self.stdout.write(self.style.WARNING(f'Skipping duplicate problem: {question}'))
                    skipped_count += 1
                    continue
                    
                # Create and save the new problem
                Problem.objects.create(
                    question=question,
                    answer=answer,
                    difficulty=prob_difficulty
                )
                created_count += 1
                self.stdout.write(f'  + Added: {question} ({prob_difficulty})')

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Failed to parse or save line "{line}": {e}'))

        self.stdout.write(self.style.SUCCESS(
            f'\nDone! Successfully added {created_count} new problems. Skipped {skipped_count} duplicates.'
        ))