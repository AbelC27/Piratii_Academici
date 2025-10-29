from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User as AuthUser
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from datetime import date, timedelta # Import timedelta
import json

from .forms import LoginForm, UserRegistrationForm
from .models import Problem, Submission, DailyChallenge, UserProfile # Import UserProfile
# --- NEW: Import the generator ---
from . import problem_generator 


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
@login_required
def daily_challenge_view(request):
    """View for daily challenge feature"""
    today_challenge = DailyChallenge.get_today_challenge()

    if not today_challenge:
        messages.warning(request, 'No daily challenge available yet. Check back later!')
        return redirect('home')

    # Check if user already completed today's challenge
    already_completed = today_challenge.is_completed_by(request.user)

    # Get user's submission history for this challenge
    user_attempts = Submission.objects.filter(
        user=request.user,
        problem=today_challenge.problem,
        submitted_at__date=date.today()
    ).order_by('-submitted_at')

    # Calculate stats
    total_completions = today_challenge.completed_by.count()

    context = {
        'challenge': today_challenge,
        'problem': today_challenge.problem,
        'already_completed': already_completed,
        'user_attempts': user_attempts,
        'total_completions': total_completions,
        'bonus_points': today_challenge.bonus_points,
    }

    return render(request, 'app/daily_challenge.html', context)


@login_required
@require_http_methods(["POST"])
def check_daily_challenge(request):
    """AJAX endpoint to check daily challenge answer"""
    try:
        data = json.loads(request.body)
        user_answer = data.get('answer', '').strip()

        today_challenge = DailyChallenge.get_today_challenge()
        if not today_challenge:
            return JsonResponse({'error': 'No challenge available'}, status=404)

        problem = today_challenge.problem

        # Check if already completed
        already_completed = today_challenge.is_completed_by(request.user)

        # --- FIX: Safe Answer Checking ---
        # The 'answer' field is a string like "579". Just cast to int.
        try:
            correct_answer = int(problem.answer)
        except ValueError:
            return JsonResponse({'error': 'Problem answer is not a valid number.'}, status=500)

        try:
            user_answer_value = int(user_answer)
        except ValueError:
            return JsonResponse({
                'correct': False,
                'message': 'Please enter a valid number',
                'correct_answer': None
            })

        is_correct = (user_answer_value == correct_answer)

        # Save submission
        Submission.objects.create(
            user=request.user,
            problem=problem,
            submitted_answer=user_answer,
            was_correct=is_correct
        )

        bonus_points_awarded = 0
        # Mark as completed if correct and not already completed
        if is_correct and not already_completed:
            today_challenge.completed_by.add(request.user)
            # Avoid adding points if already solved via normal problems view
            if request.user not in problem.solved_by.all():
                 problem.solved_by.add(request.user)

            # --- NEW: Award Bonus Points & Update Streak ---
            try:
                profile = request.user.userprofile
                bonus_points_awarded = today_challenge.bonus_points
                profile.points += bonus_points_awarded
                # --- Streak Logic (Placeholder - add fields to UserProfile first) ---
                # today = date.today()
                # if profile.last_daily_challenge_date == today - timedelta(days=1):
                #     profile.current_streak += 1
                # elif profile.last_daily_challenge_date != today: # Avoid double increment if solved same day
                #     profile.current_streak = 1
                # profile.last_daily_challenge_date = today
                profile.save()
            except UserProfile.DoesNotExist:
                pass # User profile not found, just skip
            
            message = f'🎉 Correct! Daily Challenge completed! +{bonus_points_awarded} bonus points!'
            
        elif is_correct and already_completed:
            message = '✅ Correct! (Already completed today)'
        else:
            message = '❌ Incorrect. Try again!'

        return JsonResponse({
            'correct': is_correct,
            'message': message,
            'correct_answer': correct_answer if not is_correct else None,
            'already_completed': already_completed or is_correct,
            'bonus_points': bonus_points_awarded
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

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

@login_required # Apply login_required decorator
def profile_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
        
    # --- MODIFIED: Fetch profile to show points ---
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user) # Create if missing

    # --- Fetch Streak Info (Placeholder - requires model changes) ---
    # current_streak = getattr(profile, 'current_streak', 0) 

    return render(request, 'app/profile.html', {
        'user': request.user, 
        'profile': profile,
        # 'current_streak': current_streak 
    })


@login_required
def edit_profile_view(request):
    user = request.user

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        # --- Add Avatar handling later ---
        # avatar_emoji = request.POST.get("avatar_emoji") 

        if username:
            user.username = username
        if email:
            user.email = email
        if password:
            user.set_password(password)

        # --- Save Avatar later ---
        # try:
        #    profile = user.userprofile
        #    profile.avatar = avatar_emoji 
        #    profile.save()
        # except UserProfile.DoesNotExist:
        #    pass

        user.save()
        messages.success(request, "Profilul tău a fost actualizat cu succes!")
        return redirect("profile")

    # --- Pass current Avatar later ---
    # current_avatar = getattr(user.userprofile, 'avatar', '👤')

    return render(request, "app/edit_profile.html", {
        "user": user,
        # "current_avatar": current_avatar 
    })
# Abel


# --- NEW FEATURE: My History View ---
@login_required
def my_history_view(request):
    """Show a list of the current user's past submissions."""
    submissions = Submission.objects.filter(
        user=request.user
    ).select_related('problem').order_by('-submitted_at')
    
    context = {
        'submissions': submissions
    }
    return render(request, 'app/my_history.html', context)


# Casi
from django.contrib.auth.decorators import login_required, user_passes_test


def is_admin(user):
    return user.is_staff or user.is_superuser
def problem_history_view(request):
    """Global history of solved problems (no answers shown).
    Shows one row per (user, problem) with the latest solve time.
    """
    # Filter only correct submissions
    solved_qs = Submission.objects.filter(was_correct=True)
    # Reduce to one entry per (user, problem) by taking latest submitted_at
    # Using values + annotate for portability across SQLite/Postgres
    from django.db.models import Max
    aggregated = (
        solved_qs
        .values('user__id', 'user__username', 'problem__id', 'problem__question')
        .annotate(latest_solved_at=Max('submitted_at'))
        .order_by('-latest_solved_at')[:50] # Limit to latest 50 for performance
    )

    context = {
        'entries': aggregated,
    }
    return render(request, 'app/problem_history.html', context)


@login_required
@user_passes_test(is_admin)
def admin_view(request):
    users = AuthUser.objects.all()
    total_users = users.count()
    return render(request, 'app/admin.html', {
        'users': users,
        'total_users': total_users
    })


@login_required
@user_passes_test(is_admin)
def delete_user(request, user_id):
    if not request.user.is_authenticated or not is_admin(request.user):
        return HttpResponse("Unauthorized", status=401)
    try:
        user_to_delete = AuthUser.objects.get(id=user_id)
        if user_to_delete != request.user:  # Prevent self-deletion
            user_to_delete.delete()
            messages.success(request, f'User {user_to_delete.username} has been deleted.')
        else:
            messages.error(request, 'You cannot delete your own account.')
    except AuthUser.DoesNotExist:
        messages.error(request, 'User does not exist.')
    return redirect('admin')


@login_required
@user_passes_test(is_admin)
def edit_user(request, user_id):
    if not request.user.is_authenticated or not is_admin(request.user):
        return HttpResponse("Unauthorized", status=401)
    try:
        user_to_edit = AuthUser.objects.get(id=user_id)
        if request.method == 'GET':
            return render(request, 'app/edit_user.html', {'user_to_edit': user_to_edit})
        if request.method == 'POST':
            username = request.POST.get('username')
            email = request.POST.get('email')
            if username:
                user_to_edit.username = username
            if email:
                user_to_edit.email = email

            new_password = request.POST.get('password')
            if new_password:
                user_to_edit.set_password(new_password)
            user_to_edit.save()
            messages.success(request, f'User {user_to_edit} updated')
            return redirect('admin')
    except AuthUser.DoesNotExist:
        messages.error(request, 'User does not exist.')
    return redirect('admin')


@login_required
@user_passes_test(is_admin)
def promote_user(request, user_id):
    if not request.user.is_authenticated or not is_admin(request.user):
        return HttpResponse('Unauthorized', status=401)
    try:
        user_to_promote = AuthUser.objects.get(id=user_id)
        if user_to_promote:
            # Grant staff status, but maybe not superuser unless intended
            # user_to_promote.is_superuser = True 
            user_to_promote.is_staff = True
            user_to_promote.save()
            messages.success(request, f"{user_to_promote.username} has been promoted to admin")
    except AuthUser.DoesNotExist:
        messages.error(request, 'User does not exist.')
    return redirect('admin')


@login_required
@user_passes_test(is_admin)
def demote_user(request, user_id):
    if not request.user.is_authenticated or not is_admin(request.user):
        return HttpResponse('Unauthorized', status=401)
    try:
        user_to_demote = AuthUser.objects.get(id=user_id)
        if user_to_demote != request.user: # Prevent self-demotion
            user_to_demote.is_staff = False
            user_to_demote.is_superuser = False # Ensure superuser is also removed
            user_to_demote.save()
            messages.success(request, f"{user_to_demote.username} has been demoted.")
        else:
            messages.error(request, "You cannot demote yourself.")
    except AuthUser.DoesNotExist:
        messages.error(request, 'User does not exist')
    return redirect('admin')


@login_required
def leaderboard_view(request):
    # --- FIX: Efficient Leaderboard Query ---
    # Get top 100 users ordered by points
    leaderboard_profiles = UserProfile.objects.select_related('user').order_by('-points')[:100]

    # Get stats
    total_users = AuthUser.objects.count()
    total_problems = Problem.objects.count()
    # Total solved (sum of all points) isn't as useful as total correct submissions
    total_solved = Submission.objects.filter(was_correct=True).count()

    return render(request, 'app/leaderboard.html', {
        'leaderboard': leaderboard_profiles, # Pass UserProfile objects
        'total_users': total_users,
        'total_problems': total_problems,
        'total_solved': total_solved
    })


# Codrin

# --- MODIFIED: Added Filtering ---
def problems_view(request):
    problems_qs = Problem.objects.all()
    
    # Filter by difficulty
    difficulty_filter = request.GET.get('difficulty', None)
    valid_difficulties = ['easy', 'medium', 'hard']
    if difficulty_filter and difficulty_filter.lower() in valid_difficulties:
        problems_qs = problems_qs.filter(difficulty__iexact=difficulty_filter)
        
    problems = problems_qs.order_by('-created_at') # Order after filtering

    # Get solved problem IDs for the current user
    solved_ids = []
    if request.user.is_authenticated:
        solved_ids = list(request.user.solved_problems.filter(
            # Only consider problems in the current filtered list for solved status
            id__in=[p.id for p in problems] 
        ).values_list('id', flat=True))

    return render(request, 'app/problems.html', {
        'problems': problems,
        'solved_ids': solved_ids,
        'current_difficulty': difficulty_filter # Pass filter to template
    })


@require_http_methods(["POST"])
@login_required # Require login to check answers on the main page
def check_answer(request):
    """AJAX endpoint to check if submitted answer is correct"""
    # (Rest of the check_answer function remains the same as previous version)
    # ... [omitted for brevity - use the full code from the previous response] ...
    try:
        data = json.loads(request.body)
        problem_id = data.get('problem_id')
        user_answer = data.get('answer', '').strip()

        if not problem_id or not user_answer:
            return JsonResponse({'error': 'Missing data'}, status=400)

        problem = Problem.objects.get(id=problem_id)

        # --- FIX: Safe Answer Checking ---
        try:
            # Attempt to convert both to integers for comparison
            correct_answer = int(problem.answer)
            user_answer_value = int(user_answer)
            is_correct = (user_answer_value == correct_answer)
        except ValueError:
             # If conversion fails, fallback to string comparison (less ideal but handles non-numeric answers if any)
             correct_answer_str = str(problem.answer).strip()
             is_correct = (user_answer == correct_answer_str)
             correct_answer = correct_answer_str # Ensure correct_answer sent back matches comparison type
            
        # Save submission if user is authenticated (already checked by decorator)
        Submission.objects.create(
            user=request.user,
            problem=problem,
            submitted_answer=user_answer,
            was_correct=is_correct
        )

        # Add user to solved_by list if correct and not already there
        if is_correct and request.user not in problem.solved_by.all():
            problem.solved_by.add(request.user)
            
            # --- NEW: Award Points Based on Difficulty ---
            points_to_add = 0
            # Use lower() for case-insensitive comparison
            if problem.difficulty.lower() == 'easy':
                points_to_add = 5
            elif problem.difficulty.lower() == 'medium':
                points_to_add = 10
            elif problem.difficulty.lower() == 'hard':
                points_to_add = 20
            
            if points_to_add > 0:
                try:
                    profile, created = UserProfile.objects.get_or_create(user=request.user) # Use get_or_create
                    profile.points += points_to_add
                    profile.save()
                except Exception as e: # Catch potential errors during profile update
                    print(f"Error updating profile points for {request.user.username}: {e}")
                    # Decide if you want to inform the user or just log

        return JsonResponse({
            'correct': is_correct,
            'message': '🎉 Correct!' if is_correct else '❌ Incorrect. Try again!',
            'correct_answer': correct_answer if not is_correct else None # Send back the comparison value
        })

    except Problem.DoesNotExist:
        return JsonResponse({'error': 'Problem not found'}, status=404)
    except Exception as e:
        # Log the full error for debugging
        import traceback
        print(f"Error in check_answer: {e}")
        traceback.print_exc() 
        return JsonResponse({'error': 'An unexpected error occurred. Please try again.'}, status=500)

# --- NEW: Practice View using Generator ---
@login_required # Or remove if you want anonymous users to practice
def practice_view(request):
    """
    Displays dynamically generated problems for practice.
    Does not save submissions or award points.
    """
    difficulty = request.GET.get('difficulty', 'easy') # Default to easy
    valid_difficulties = ['easy', 'medium', 'hard']
    if difficulty.lower() not in valid_difficulties:
        difficulty = 'easy' # Fallback to easy if invalid difficulty provided

    num_problems = 5 # Generate 5 problems at a time
    generated_problems = []
    for i in range(num_problems):
        # Add a unique ID for the template to track each problem
        problem_data = problem_generator.generate_arithmetic_problem(difficulty)
        problem_data['practice_id'] = f"p{i+1}" # e.g., p1, p2, ...
        generated_problems.append(problem_data)

    context = {
        'generated_problems': generated_problems,
        'current_difficulty': difficulty,
    }
    return render(request, 'app/practice.html', context)