from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User as AuthUser
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from datetime import date, timedelta # Import timedelta
import json

from .forms import LoginForm, UserRegistrationForm, ProblemForm
# --- IMPORT SpeedRunAttempt ---
from .models import Problem, Submission, DailyChallenge, UserProfile, SpeedRunAttempt, MapCheckpoint, UserProgress
# --- NEW: Import the generator ---
from . import problem_generator 
from django.shortcuts import get_object_or_404


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
    
    # --- NEW: Get current streak ---
    current_streak = 0
    try:
        current_streak = request.user.userprofile.current_streak
    except UserProfile.DoesNotExist:
        pass # Will be 0

    context = {
        'challenge': today_challenge,
        'problem': today_challenge.problem,
        'already_completed': already_completed,
        'user_attempts': user_attempts,
        'total_completions': total_completions,
        'bonus_points': today_challenge.bonus_points,
        'current_streak': current_streak, # <-- Pass streak to template
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
            # --- FALLBACK FOR NON-INT ANSWERS (like fractions) ---
            try:
                # Try float
                correct_answer = float(problem.answer)
            except ValueError:
                # Fallback to string
                correct_answer = str(problem.answer)


        try:
            user_answer_value = int(user_answer)
        except ValueError:
             try:
                 user_answer_value = float(user_answer)
             except ValueError:
                 user_answer_value = str(user_answer)

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
                
                # --- Streak Logic (UNCOMMENTED AND IMPLEMENTED) ---
                today = date.today()
                if profile.last_daily_challenge_date == today - timedelta(days=1):
                    # Streak continues
                    profile.current_streak += 1
                elif profile.last_daily_challenge_date != today: # Avoid double increment if solved same day
                    # Reset or start streak
                    profile.current_streak = 1
                
                profile.last_daily_challenge_date = today
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
# ... (imports remain the same) ...

# Andi, Sergiu, etc views remain the same

@login_required # Apply login_required decorator
def profile_view(request):
    # ... (this view remains the same, profile object already has avatar) ...
    if not request.user.is_authenticated:
        return redirect('login')

    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user) # Create if missing

    current_streak = getattr(profile, 'current_streak', 0)

    return render(request, 'app/profile.html', {
        'user': request.user,
        'profile': profile,
        'current_streak': current_streak
    })


@login_required
def edit_profile_view(request):
    user = request.user
    # --- GET PROFILE FOR CURRENT AVATAR ---
    try:
        profile = user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=user)

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        # --- GET AVATAR ---
        avatar_emoji = request.POST.get("avatar_emoji")

        error_occurred = False # Flag to prevent redirect if validation fails

        # --- Basic Avatar Validation ---
        if avatar_emoji:
            # Simple check: is it likely an emoji? (Very basic check)
            # More robust validation might involve checking Unicode ranges
            if len(avatar_emoji) > 2 and not avatar_emoji.startswith((':', '<')): # Avoid things like :smile: or <img..>
                 profile.avatar = avatar_emoji[0] # Try taking the first char if too long
                 # You could add a message here: messages.warning(request, "Avatar trimmed.")
            elif len(avatar_emoji) <= 2 and len(avatar_emoji)>0:
                 profile.avatar = avatar_emoji
            else:
                 messages.error(request, "Invalid Avatar format. Please use a single emoji.")
                 error_occurred = True
        else:
             # Option: Set default if empty, or keep current
             profile.avatar = '👤' # Reset to default if submitted empty

        # --- Update User Fields ---
        if username and username != user.username:
            # Add validation if needed (e.g., check if username exists)
            user.username = username
        if email != user.email:
            # Add validation if needed (e.g., check if email exists)
            user.email = email
        if password:
            # Add password validation if desired
            user.set_password(password)

        if not error_occurred:
            user.save()
            profile.save() # Save profile changes (avatar)
            messages.success(request, "Profilul tău a fost actualizat cu succes!")
            return redirect("profile")
        # If error occurred, fall through to render the form again with error messages

    current_avatar = profile.avatar # Pass current avatar to template

    return render(request, "app/edit_profile.html", {
        "user": user,
        "current_avatar": current_avatar # Pass current avatar
    })

# ... (rest of the views remain the same) ...

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

# --- MODIFIED: Added Category Filtering ---
def problems_view(request):
    problems_qs = Problem.objects.all()
    
    # --- Get all categories for filter bar ---
    all_categories = Problem.CATEGORY_CHOICES
    
    # Filter by difficulty
    difficulty_filter = request.GET.get('difficulty', None)
    valid_difficulties = ['easy', 'medium', 'hard']
    if difficulty_filter and difficulty_filter.lower() in valid_difficulties:
        problems_qs = problems_qs.filter(difficulty__iexact=difficulty_filter)

    # --- NEW: Filter by category ---
    category_filter = request.GET.get('category', None)
    valid_categories = [c[0] for c in all_categories]
    if category_filter and category_filter.lower() in valid_categories:
        problems_qs = problems_qs.filter(category__iexact=category_filter)
        
    problems = problems_qs.order_by('id') # Order after filtering

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
        'current_difficulty': difficulty_filter,
        'all_categories': all_categories,         # <-- Pass categories
        'current_category': category_filter,      # <-- Pass current category
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
             # If conversion fails, try floats
             try:
                correct_answer = float(problem.answer)
                user_answer_value = float(user_answer)
                is_correct = (user_answer_value == correct_answer)
             except ValueError:
                # Fallback to string comparison (handles fractions like '2/3')
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


# --- ADD THESE 3 NEW VIEWS FOR SPEED RUN ---

@login_required
def speed_run_view(request):
    """
    Renders the main page for the Speed Run game.
    """
    # Get user's high score
    high_score = SpeedRunAttempt.objects.filter(user=request.user).order_by('-score').first()
    context = {
        'high_score': high_score.score if high_score else 0
    }
    return render(request, 'app/speed_run.html', context)

@login_required
@require_http_methods(["GET"])
def get_generated_problem_api(request):
    """
    API endpoint to fetch a single, dynamically generated 'easy' problem.
    """
    try:
        # We use 'easy' for speed run mode
        problem_data = problem_generator.generate_arithmetic_problem('easy')
        return JsonResponse(problem_data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["POST"])
def save_speed_run_view(request):
    """
    API endpoint to save a user's speed run score.
    """
    try:
        data = json.loads(request.body)
        score = int(data.get('score', 0))

        if score < 0:
            return JsonResponse({'error': 'Invalid score'}, status=400)

        # Save the attempt
        attempt = SpeedRunAttempt.objects.create(user=request.user, score=score)

        # Check if it's a new high score
        high_score = SpeedRunAttempt.objects.filter(user=request.user).order_by('-score').first().score
        
        return JsonResponse({
            'status': 'success', 
            'score_saved': attempt.score,
            'high_score': high_score
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# -----------------------------------------------


@login_required
@user_passes_test(is_admin)
def admin_problem_list(request):
    """Lists all problems for admin management."""
    problems = Problem.objects.order_by('-created_at')
    context = {'problems': problems}
    return render(request, 'app/admin_problem_list.html', context)

@login_required
@user_passes_test(is_admin)
def admin_problem_add(request):
    """Handles adding a new problem."""
    if request.method == 'POST':
        form = ProblemForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Problem added successfully!')
            return redirect('admin_problem_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProblemForm()

    context = {'form': form, 'form_title': 'Add New Problem'}
    return render(request, 'app/admin_problem_form.html', context)

@login_required
@user_passes_test(is_admin)
def admin_problem_edit(request, problem_id):
    """Handles editing an existing problem."""
    problem = get_object_or_404(Problem, id=problem_id)
    if request.method == 'POST':
        form = ProblemForm(request.POST, instance=problem)
        if form.is_valid():
            form.save()
            messages.success(request, f'Problem #{problem_id} updated successfully!')
            return redirect('admin_problem_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProblemForm(instance=problem)

    context = {'form': form, 'problem': problem, 'form_title': f'Edit Problem #{problem_id}'}
    return render(request, 'app/admin_problem_form.html', context)

@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"]) # Ensure this view only handles POST requests for safety
def admin_problem_delete(request, problem_id):
    """Handles deleting a problem."""
    problem = get_object_or_404(Problem, id=problem_id)
    try:
        problem_question = problem.question # Get question before deleting
        problem.delete()
        messages.success(request, f'Problem "{problem_question}" deleted successfully!')
    except Exception as e:
        messages.error(request, f'Error deleting problem: {e}')
    return redirect('admin_problem_list')

# ========================================
# PIRATE MAP JOURNEY FEATURE
# ========================================

@login_required
def pirate_map_view(request):
    """
    Display the pirate map with all checkpoints and user's current progress.
    """
    # Get or create user progress
    user_progress, created = UserProgress.objects.get_or_create(
        user=request.user,
        defaults={'current_checkpoint': MapCheckpoint.objects.filter(checkpoint_number=1).first()}
    )
    
    # Get all checkpoints
    all_checkpoints = MapCheckpoint.objects.all().order_by('checkpoint_number')
    
    # Determine which checkpoints are unlocked
    checkpoints_data = []
    for checkpoint in all_checkpoints:
        is_current = (user_progress.current_checkpoint == checkpoint)
        is_unlocked = (checkpoint.checkpoint_number <= user_progress.current_checkpoint.checkpoint_number 
                      if user_progress.current_checkpoint else False)
        is_completed = (checkpoint.checkpoint_number < user_progress.current_checkpoint.checkpoint_number
                       if user_progress.current_checkpoint else False)
        
        checkpoints_data.append({
            'checkpoint': checkpoint,
            'is_current': is_current,
            'is_unlocked': is_unlocked,
            'is_completed': is_completed,
        })
    
    # Get available problems for current checkpoint (filter by difficulty)
    current_problems = []
    if user_progress.current_checkpoint:
        # Map difficulty level to problem difficulty
        difficulty_map = {
            1: 'easy',
            2: 'easy',
            3: 'medium',
            4: 'medium',
            5: 'hard',
        }
        target_difficulty = difficulty_map.get(user_progress.current_checkpoint.difficulty_level, 'easy')
        current_problems = Problem.objects.filter(difficulty=target_difficulty).order_by('?')[:10]
    
    context = {
        'user_progress': user_progress,
        'checkpoints': checkpoints_data,
        'current_checkpoint': user_progress.current_checkpoint,
        'current_problems': current_problems,
        'progress_percentage': (user_progress.problems_solved_at_current / 
                               user_progress.current_checkpoint.problems_to_unlock * 100) 
                               if user_progress.current_checkpoint else 0,
        'can_advance': user_progress.can_advance(),
    }
    
    return render(request, 'app/pirate_map.html', context)


@login_required
@require_http_methods(["POST"])
def solve_map_problem(request):
    """
    AJAX endpoint to check answer for a problem in the pirate map journey.
    If correct, it records progress and may advance the checkpoint.
    """
    try:
        data = json.loads(request.body)
        problem_id = data.get('problem_id')
        user_answer = data.get('answer', '').strip()
        
        if not problem_id or not user_answer:
            return JsonResponse({'error': 'Missing data'}, status=400)
        
        problem = Problem.objects.get(id=problem_id)
        user_progress = UserProgress.objects.get(user=request.user)
        
        # Evaluate the correct answer
        try:
            correct_answer = eval(problem.answer, {"__builtins__": None}, {})
        except:
            correct_answer = int(problem.answer)
        
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
        
        # Save submission
        Submission.objects.create(
            user=request.user,
            problem=problem,
            submitted_answer=user_answer,
            was_correct=is_correct
        )
        
        response_data = {
            'correct': is_correct,
            'correct_answer': correct_answer if not is_correct else None,
            'advanced': False,
            'checkpoint_completed': False,
        }
        
        if is_correct:
            # Add to solved problems if not already there
            if request.user not in problem.solved_by.all():
                problem.solved_by.add(request.user)
            
            # Record progress
            advanced = user_progress.record_problem_solved()
            
            response_data['advanced'] = advanced
            response_data['checkpoint_completed'] = user_progress.can_advance() and not advanced
            response_data['problems_solved'] = user_progress.problems_solved_at_current
            response_data['problems_needed'] = user_progress.current_checkpoint.problems_to_unlock if user_progress.current_checkpoint else 0
            
            if advanced:
                response_data['message'] = f'🎉 Checkpoint completed! Welcome to {user_progress.current_checkpoint.name}! +{user_progress.current_checkpoint.previous_checkpoint.points_reward if user_progress.current_checkpoint.previous_checkpoint else 0} points!'
                response_data['new_checkpoint'] = {
                    'name': user_progress.current_checkpoint.name,
                    'emoji': user_progress.current_checkpoint.emoji,
                    'number': user_progress.current_checkpoint.checkpoint_number,
                }
            elif user_progress.can_advance():
                response_data['message'] = f'🎉 Correct! You can now advance to the next checkpoint!'
            else:
                remaining = user_progress.current_checkpoint.problems_to_unlock - user_progress.problems_solved_at_current
                response_data['message'] = f'🎉 Correct! {remaining} more to unlock next checkpoint!'
        else:
            response_data['message'] = '❌ Incorrect. Try again, matey!'
        
        return JsonResponse(response_data)
        
    except Problem.DoesNotExist:
        return JsonResponse({'error': 'Problem not found'}, status=404)
    except UserProgress.DoesNotExist:
        return JsonResponse({'error': 'User progress not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def advance_checkpoint(request):
    """
    AJAX endpoint to manually advance to next checkpoint if requirements are met.
    """
    try:
        user_progress = UserProgress.objects.get(user=request.user)
        
        if not user_progress.can_advance():
            return JsonResponse({
                'success': False,
                'message': 'You haven\'t solved enough problems yet!'
            })
        
        advanced = user_progress.advance_to_next_checkpoint()
        
        if advanced:
            return JsonResponse({
                'success': True,
                'message': f'⚓ Welcome to {user_progress.current_checkpoint.name}!',
                'new_checkpoint': {
                    'name': user_progress.current_checkpoint.name,
                    'emoji': user_progress.current_checkpoint.emoji,
                    'number': user_progress.current_checkpoint.checkpoint_number,
                    'description': user_progress.current_checkpoint.description,
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'No more checkpoints available. You\'ve completed the journey! 🏆'
            })
            
    except UserProgress.DoesNotExist:
        return JsonResponse({'error': 'User progress not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
