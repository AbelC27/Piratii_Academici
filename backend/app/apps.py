from django.apps import AppConfig
import os # <-- Import os

class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'

    # --- ADD THIS WHOLE 'ready' METHOD ---
    def ready(self):
        """
        Run code once when the server starts.
        """
        # We check for 'RUN_MAIN' to avoid this running twice (once for main,
        # once for the reloader process).
        if os.environ.get('RUN_MAIN'):
            print("--- PBMate App Ready ---")
            
            from django.core.management import call_command
            from .models import Problem

            # 1. Ensure today's daily challenge exists
            try:
                print("Checking for today's daily challenge...")
                call_command('create_daily_challenge')
            except Exception as e:
                print(f"Error creating daily challenge: {e}")

            # 2. Check if the problem database is empty
            if not Problem.objects.exists():
                print("Database is empty. Populating problems...")
                
                try:
                    # First, run the basic populate script
                    print("Running populate_problems...")
                    call_command('populate_problems')
                except Exception as e:
                    print(f"Error running populate_problems: {e}")

                try:
                    # Second, run the AI generator for 10 problems
                    print("Running generate_ai_problems...")
                    call_command('generate_ai_problems', count=10, difficulty='easy')
                    call_command('generate_ai_problems', count=10, difficulty='medium')
                except Exception as e:
                    print(f"Error running generate_ai_problems: {e}")
                
                print("Database population complete.")
            else:
                print("Database already contains problems. Skipping population.")
            
            print("--- Server startup checks complete ---")