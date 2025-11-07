from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('signup/success/', views.signup_success_view, name='signup_success'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('problems/', views.problems_view, name='problems'), # Existing problems from DB
    path('practice/', views.practice_view, name='practice'),
    
    # --- SPEED RUN ---
    path('speed-run/', views.speed_run_view, name='speed_run'),
    path('api/get-generated-problem/', views.get_generated_problem_api, name='get_generated_problem_api'),
    path('api/save-speed-run/', views.save_speed_run_view, name='save_speed_run'),
    # --------------------------------------

    path('api/check-answer/', views.check_answer, name='check_answer'), # Checks DB problems
    
    # Pirate Map Journey
    path('pirate-map/', views.pirate_map_view, name='pirate_map'),
    path('api/solve-map-problem/', views.solve_map_problem, name='solve_map_problem'),
    path('api/advance-checkpoint/', views.advance_checkpoint, name='advance_checkpoint'),
    
    path('daily-challenge/', views.daily_challenge_view, name='daily_challenge'),
    path('api/check-daily-challenge/', views.check_daily_challenge, name='check_daily_challenge'),
    path('leaderboard/', views.leaderboard_view, name = 'leaderboard'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    path('problem-history/', views.problem_history_view, name='problem_history'),
    path('my-history/', views.my_history_view, name='my_history'),
    
    path('admin-dashboard/', views.admin_view, name='admin'),
    path('manage/edit/<int:user_id>/', views.edit_user, name='edit_user'),
    path('manage/promote/<int:user_id>/', views.promote_user, name='promote_admin'),
    path('manage/demote/<int:user_id>/', views.demote_user, name='demote_admin'),
    path('manage/delete/<int:user_id>/', views.delete_user, name='delete_user'),

    path('dashboard/', views.admin_view, name='admin'),
    # path('dashboard/problems/', views.admin_problem_list, name='admin_problem_list'), # TODO: Implement admin_problem views
    # path('dashboard/problems/add/', views.admin_problem_add, name='admin_problem_add'),
    # path('dashboard/problems/edit/<int:problem_id>/', views.admin_problem_edit, name='admin_problem_edit'),
    # path('dashboard/problems/delete/<int:problem_id>/', views.admin_problem_delete, name='admin_problem_delete'),
]