from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User as AuthUser
from .forms import LoginForm
from django.contrib import messages
from django.http import HttpResponse
from .forms import UserRegistrationForm

# Andi

def signup_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Account created successfully for {user.username}! You can now log in.')
            return redirect('signup_success')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'app/signup.html', {'form': form})


def signup_success_view(request):
    return render(request, 'app/signup_success.html')


# Sergiu
def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                form.add_error(None, "Invalid username or password")

    else:
        form = LoginForm()
    return render(request, 'app/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')
def home_view(request):
    return render(request, 'app/home.html')





# Abel







# Casi







# Codrin
from .models import Problem, Submission
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json

def problems_view(request):
    problems = Problem.objects.all().order_by('-created_at')
    
    # Get solved problem IDs for the current user
    solved_ids = []
    if request.user.is_authenticated:
        solved_ids = list(request.user.solved_problems.values_list('id', flat=True))
    
    return render(request, 'app/problems.html', {
        'problems': problems,
        'solved_ids': solved_ids
    })

@require_http_methods(["POST"])
def check_answer(request):
    """AJAX endpoint to check if submitted answer is correct"""
    try:
        data = json.loads(request.body)
        problem_id = data.get('problem_id')
        user_answer = data.get('answer', '').strip()
        
        if not problem_id or not user_answer:
            return JsonResponse({'error': 'Missing data'}, status=400)
        
        problem = Problem.objects.get(id=problem_id)
        
        # Evaluate the correct answer
        try:
            correct_answer = eval(problem.answer, {"__builtins__": None}, {})
        except:
            correct_answer = int(problem.answer)  # Fallback if already a number
        
        # Evaluate user answer
        try:
            user_answer_value = int(user_answer)
        except ValueError:
            return JsonResponse({
                'correct': False,
                'message': 'Please enter a valid number',
                'correct_answer': correct_answer
            })
        
        is_correct = (user_answer_value == correct_answer)
        
        # Save submission if user is authenticated
        if request.user.is_authenticated:
            Submission.objects.create(
                user=request.user,
                problem=problem,
                submitted_answer=user_answer,
                was_correct=is_correct
            )
            
            # Add user to solved_by list if correct and not already there
            if is_correct and request.user not in problem.solved_by.all():
                problem.solved_by.add(request.user)
        
        return JsonResponse({
            'correct': is_correct,
            'message': '🎉 Correct!' if is_correct else '❌ Incorrect. Try again!',
            'correct_answer': correct_answer if not is_correct else None
        })
        
    except Problem.DoesNotExist:
        return JsonResponse({'error': 'Problem not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
