import random

def generate_arithmetic_problem(difficulty='easy'):
    """
    Generates a simple arithmetic problem (addition, subtraction, multiplication).
    Ensures answers are non-negative.
    """
    if difficulty == 'easy':
        num1 = random.randint(1, 10)
        num2 = random.randint(1, 10)
        operator = random.choice(['+', '-', '*'])
    elif difficulty == 'medium':
        num1 = random.randint(10, 50)
        num2 = random.randint(5, 25)
        operator = random.choice(['+', '-', '*', '+', '-']) # More + and -
    elif difficulty == 'hard':
        num1 = random.randint(20, 100)
        num2 = random.randint(10, 50)
        operator = random.choice(['+', '-', '*', '*', '*']) # More *
    else: # Default to easy
        num1 = random.randint(1, 10)
        num2 = random.randint(1, 10)
        operator = random.choice(['+', '-', '*'])

    # Ensure subtraction doesn't result in negative numbers easily
    if operator == '-':
        # Swap numbers if num1 < num2 to keep answers positive more often
        if num1 < num2:
            num1, num2 = num2, num1 
        # For easy, ensure result isn't negative
        if difficulty == 'easy' and num1 == num2:
             num1 += random.randint(1, 5) # Avoid zero answer often

    question = f"{num1} {operator} {num2}"
    
    # Calculate answer safely
    answer = 0
    if operator == '+':
        answer = num1 + num2
    elif operator == '-':
        answer = num1 - num2
    elif operator == '*':
        answer = num1 * num2
        
    # Replace Python '*' with '×' for display
    display_question = question.replace('*', '×')

    return {
        'question': display_question, 
        'answer': str(answer),       # Store answer as string, like DB problems
        'difficulty': difficulty
    }

# Example usage (for testing):
if __name__ == '__main__':
    print("Easy:", generate_arithmetic_problem('easy'))
    print("Medium:", generate_arithmetic_problem('medium'))
    print("Hard:", generate_arithmetic_problem('hard'))
