from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('signup/success/', views.signup_success_view, name='signup_success'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('problems/', views.problems_view, name='problems'), # Existing problems from DB
    path('practice/', views.practice_view, name='practice'), # <-- ADD THIS LINE for generated problems
    path('api/check-answer/', views.check_answer, name='check_answer'), # Checks DB problems
    
    path('daily-challenge/', views.daily_challenge_view, name='daily_challenge'),
    path('api/check-daily-challenge/', views.check_daily_challenge, name='check_daily_challenge'),
    path('leaderboard/', views.leaderboard_view, name = 'leaderboard'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    path('problem_history/', views.problem_history_view, name='problem_history'),
    path('my-history/', views.my_history_view, name='my_history'), 
    
    path('admin-dashboard/', views.admin_view, name='admin'),
    path('manage/edit/<int:user_id>/', views.edit_user, name='edit_user'),
    path('manage/promote/<int:user_id>/', views.promote_user, name='promote_admin'),
    path('manage/demote/<int:user_id>/', views.demote_user, name='demote_admin'),
    path('manage/delete/<int:user_id>/', views.delete_user, name='delete_user'),

    path('dashboard/', views.admin_view, name='admin'),
    path('dashboard/problems/', views.admin_problem_list, name='admin_problem_list'),
    path('dashboard/problems/add/', views.admin_problem_add, name='admin_problem_add'),
    path('dashboard/problems/edit/<int:problem_id>/', views.admin_problem_edit, name='admin_problem_edit'),
    path('dashboard/problems/delete/<int:problem_id>/', views.admin_problem_delete, name='admin_problem_delete'),
]
